实例化工作流
========================

我们的 BPMN 引擎 (:app:`engine/engine.py`) 的 :code:`start_workflow` 方法:

.. code-block:: python

    def start_workflow(self, spec_id):
        spec, sp_specs = self.serializer.get_workflow_spec(spec_id)
        wf = BpmnWorkflow(spec, sp_specs, script_engine=self._script_engine)
        wf_id = self.serializer.create_workflow(wf, spec_id)
        return wf_id

我们将使用序列化程序根据id 重新创建工作流规范。
如parsing_subprocesses中所述，流程有一个顶级规范和流程 id->spec 字典，其中包含顶级流程引用的任何其他流程（调用Actitivies和subprocesses）。

运行工作流
==================

在最简单的情况下，运行工作流需要实现以下循环：

* 运行任何 `READY`引擎任务 (where :code:`task_spec.manual == False`)
* 向用户显示`READY`人工任务（如果有）
* 如有必要，更新人工任务数据
* 运行人工任务
* 刷新任何 `WAITING`任务

直到没有任务要完成为止。

以下是我们的引擎方法：

.. code-block:: python

    def run_until_user_input_required(self, workflow):
        task = workflow.get_next_task(state=TaskState.READY, manual=False)
        while task is not None:
            task.run()
            self.run_ready_events(workflow)
            task = workflow.get_next_task(state=TaskState.READY, manual=False)

    def run_ready_events(self, workflow):
        workflow.refresh_waiting_tasks()
        task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        while task is not None:
            task.run()
            task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)

在第一个步骤中，我们检索并运行任何可以自动执行的任务，包括处理可能发生的任何事件。

第二种方法处理事件。
与事件相对应的任务仍处于状态 :code:`WAITING` 直到它捕捉到它正在等待的任何事件，这时它就变成了 :code:`READY` 并且可以运行。
这个:code:`workflow.refresh_waiting_tasks` 方法迭代所有等待的任务，如果已经满足这样做的条件, 并将状态更改为 :code:`READY`。

我们将使用 `workflow.get_next_task` 方法和处理本文档后面的人工任务。

任务
=====

在本节中，我们将概述任务规范的一些常规属性，然后深入研究一些特定类型。
请参阅 :ref:`specs_vs_instances` 以阅读有关任务与任务规范的信息。

BPMN任务规范
---------------

BPMN任务规范 :code:`SpiffWorkflow.specs.base.TaskSpec` 继承了相当多的属性, 但你可能不必太关注其中的大部分。
其中一些重要的是：

* `name`:TaskSpec的唯一id，并且它将对应于BPMN id（如果存在）
* `description`: 我们使用该属性来提供 BPMN 任务类型的描述
* `manual`: :code:`True` 如果需要人工输入来完成与此任务规范关联的任务

BPMN任务规范具有以下附加属性:

* `bpmn_id`: BPMN任务的ID (如果任务在图表上不可见，则为 :code:`None`)
* `bpmn_name`: 任务的BPMN名称
* `lane`: BPMN任务的通道
* `documentation`: 任务的BPMN `documentation`  元素的内容


在示例应用程序中，我们使用以下 :code:`bpmn_name` (或 :code:`name` 当:code:`bpmn_name` 未指定时),
及 :code:`lane` 显示有关工作流中任务的信息 (在 :app:`curses_ui/workflow_view.py` 查看 :code:`update_task_tree` 方法).

这个 :code:`manual` 属性特别重要，因为SpiffWorkflow不包括内置这些任务的处理，因此您需要将其作为应用程序的一部分来实现。
我们将在下一节中介绍如何在此应用程序中处理此问题。


.. note::

    SpiffWorkflow将非任务（没有分配更具体类型的BPMN任务）视为手动任务。

实例化的任务
------------------

实际上，所有的任务都是实例化的--这就是任务与任务规范的区别；然而，我们不可能过多地重复这一点。

任务具有一些附加属性，其中包含有关特定实例的重要详细信息：

* :code:`id`: 唯一标识任务的UUID（请记住，可以多次访问任务规范，但每次都会创建一个新任务）
* :code:`task_spec`: 与此任务关联的任务规范
* :code:`state`: 任务的状态，代表在 :code:`TaskState`中的一个值
* :code:`last_state_change`: 此任务上次更改状态的时间戳
* :code:`data`: 保存任务/工作流数据的字典

人工（用户和手动）任务
-----------------------------

请记住 :code:`bpmn` 模块不提供用于从用户收集信息的任何默认能力，这是你必须实现的。
在本例中，我们将假设使用的是
:code:`spiff` 模块（在:code:`camunda`模块中有一个替代实现）。

Spiff Arena使用JSON模式定义与用户任务和
`react-jsonschema-form <https://github.com/rjsf-team/react-jsonschema-form>`_ 以渲染它们。
此外，我们的用户和手册任务有一个自定义扩展 :code:`instructionsForEndUser` 其存储使用任务数据呈现的具有Markdown格式的Jinja模板。
可以使用不同的格式来定义表单，根据应用程序的需要，Jinja和Markdown可以很容易地被其他模板和呈现方案所取代。

我们的用户和手动任务处理程序呈现指令（此代码来自 :app:`spiff/curses_handlers.py`）:

.. code-block:: python

    from jinja2 import Template

    def get_instructions(self):
        instructions = f'{self.task.task_spec.bpmn_name}\n\n'
        text = self.task.task_spec.extensions.get('instructionsForEndUser')
        if text is not None:
            template = Template(text)
            instructions += template.render(self.task.data)
        instructions += '\n\n'
        return instructions

我们不会试图在curses UI中处理Markdown，所以我们假设我们只有文本。
然而，我们确实希望能够将特定于工作流的数据纳入呈现给用户的信息中；这是您的应用程序肯定需要做的事情。
在这里，我们使用Task的 :code:`data` 属性（记住这是一个字典）来呈现模板。

我们的应用程序包含一个 :code:`Field` 类（在 :app:`curses_ui/user_input.py` 中定义），
它告诉我们如何转换为字符串表示和从字符串表示转换，该字符串表示可以显示在屏幕上，并可以与表单显示屏幕交互。
我们的用户任务处理程序还提供了一种方法，用于将几个基本的JSON模式类型转换为可以显示的内容（仅支持文本、整数和“oneOf”）。
表单屏幕收集并验证用户输入，并将结果收集到字典中。

我们不会详细介绍表单屏幕是如何工作的，因为它是特定于这个应用程序的，而不是库本身；
相反，我们将跳到在任务呈现给用户后运行该任务的代码；任何应用程序都需要这样做。

对于“手动任务”，仅运行任务就足够了。

.. code-block:: python

    def on_complete(self, results):
        self.task.run()

但是，我们需要将此方法扩展到用户任务，以将用户提交的数据合并到工作流中：

.. code-block:: python

    def on_complete(self, results):
        self.task.set_data(**results)
        super().on_complete(results)

这里我们为表单中的每个字段设置一个键。
这里的其他可能选项是设置一个包含所有表单数据的键，或者将架构映射到Python类并使用它来代替字典。
最好的管理方式由您决定。

这里的关键点是，您的应用程序需要能够显示信息，可能会合并工作流实例中的数据，并根据用户输入更新这些数据。
接下来我们将学习一个简单的例子。

我们将参考 :bpmn:`task_types.bpmn` 中建模的流程，该流程包含一个简单的表单，要求用户输入产品和数量，
以及一个在流程结束时显示订单信息的手动任务（该表单定义为:form:`select_product_and_quantity.json`)

用户提交表单后，我们将在以下词典中收集结果：

.. code-block:: python

    {
        'product_name': 'product_a',
        'product_quantity': 2,
    }

我们将在运行任务之前将这些变量添加到任务数据中。
“业务规则”任务根据 :code:`product_name` 从DMN表中查找价格，而脚本任务则根据价格和数量设置 :code:`order_total` 。

我们的手动任务说明如下：

.. code-block::

    Order Summary
    {{ product_name }}
    Quantity: {{ product_quantity }}
    Order Total: {{ order_total }}

并且当针对实例数据呈现时反映该特定顺序的细节。

业务规则任务
-------------------

业务规则任务未在 :code:`SpiffWorkflow.bpmn` 模块中实现；
但是，该库在 :code:`SpiffWorkflow.dmn` 模块中确实包含业务规则任务的DMN实现。
:code:`spiff` 和 :code:`camunda` 模块都支持DMN。

网关
--------

您不需要特殊的代码来处理网关（这是该库为您做的事情之一），但值得强调的是，网关条件被视为Python表达式，根据任务数据的上下文进行计算。
有关更多详细信息，请参阅 :doc:`script_engine` 。


脚本和服务任务
------------------------

有关Spiff如何处理这些任务的更多信息，请参阅:doc:`script_engine`。
没有默认的服务任务实现，但我们将介绍一个在那里实现的方法示例。
脚本任务假定:code:`script` 属性包含Python脚本的文本，该脚本在任务数据的上下文中执行。

.. _task_filters:

筛选任务
===============

SpiffWorkflow有两种检索任务的方法：

- :code:`workflow.get_tasks`: 返回匹配任务的列表或空列表
- :code:`workflow.get_next_task`: 返回第一个匹配的任务，或 None

这两个方法都使用相同的辅助类，并采用相同的参数——唯一的区别是返回类型。

这些方法返回一个 :code:`TaskIterator`，然后使用一个 :code:`TaskFilter`来确定匹配的任务。


任务可以通过以下方式进行筛选：

- :code:`state`: 一个:code:`TaskState` 值（有关可能的状态，请参阅 :ref:`states'）
- :code:`spec_name`: 任务规范的名称（通常对应于BPMN ID）
- :code:`manual`: 任务规范是否需要手动输入
- :code:`updated_ts`: 将结果限制在提供的时间戳之后
- :code:`spec_class`: 将结果限制为特定的任务规范类
- :code:`lane`: 任务规范的通道
- :code:`catches_event`: 捕获特定代码的任务规范 :code:`BpmnEvent`

示例
--------

我们在此参考以下流程：

- :bpmn:`top_level.bpmn`
- :bpmn:`call_activity.bpmn`

要按状态进行筛选，我们需要导入 :code:`TaskState`对象（除非您想记住哪些数字对应于哪些状态）。


.. code-block:: python

    from SpiffWorkflow.util.task import TaskState

准备好的人工任务
^^^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(state=TaskState.READY, manual=False)

已完成的任务
^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(state=TaskState.COMPLETED)

按规范名称列出的任务
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(spec_name='customize_product')

将返回一个列表，其中包含用于在我们的示例工作流中定制产品的Call Activities 。


任务更新时间
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    ts = datetime.now() - timedelta(hours=1)
    tasks = workflow.get_tasks(state=TaskState.WAITING, updated_ts=ts)

返回在过去一小时内更改为 :code:`WAITING` 的任务。

按通道划分的任务
^^^^^^^^^^^^^

.. code:: python

     ready_tasks = workflow.get_tasks(state=TaskState.READY, lane='Customer')

在我们的示例工作流中，将只返回'Customer'通道中的任务。

子流程和呼叫活动
================================

在本文档的第一节中，我们注意到 :code:`BpmnWorkflow` 是用顶级规范以及任何引用进程的规范集合实例化的。
实例化的 :code:`BpmnSubWorkflows` 被维护为 :code:`subprocesses` 属性中的 :code:`task.id` 到 :code:`BpmnSubworkflow` 的映射。

这两个类都继承自 :code:`Workflow` ，并在单独的任务树中维护任务。
但是，只有 :code:`BpmnWorkflow` 维护子工作流信息；甚至深度嵌套的工作流也存储在顶层（以便于访问）。

任务迭代的工作方式也不同。:code:`Bpmworkflow.get_tasks` 已扩展为检索与任务相关联的子工作流，并对这些子工作流进行迭代；
在 :code:`BpmnSubWorkflow` 中迭代任务时，将只返回该工作流中的任务。

.. code-block:: python

    task = workflow.get_next_task(spec_name='customize_product')
    subprocess = workflow.get_subprocess(task)
    subprocess_tasks = subprocess.get_tasks()

此代码块查找示例工作流的第一个产品自定义，并仅获取该工作流中的任务。

:code:`BpmnSubworkflow` 始终使用顶级工作流的脚本引擎，以确保一致性。

此外，该类还有一些额外的属性，可以更方便地在嵌套工作流中导航：

- :code:`subworkflow.top_workflow` 返回顶级工作流
- :code:`subworkflow.parent_task_id` 返回与工作流关联的任务的UUID
- :code:`parent_workflow`: 返回堆栈中位于其正上方的工作流

这些方法也存在于顶级工作流中，并返回 :code:`None` .

事件
======

BPMN事件由 :code:`BpmnEvent` 类表示。
此类的一个实例包含一个 :code:`EventDefinition` 、一个可选的有效负载、定义它们的消息的消息相关性，以及（也可选）一个目标子工作流。
最后一个属性由SpiffWorkflow内部由需要与其他子工作流通信的子工作流使用, 并且可以被安全地忽略。

:code:`EventDefinition` 和 :code:`BpmnEvent` BpmnEvent之间的关系类似于 :code:`TaskSpec` 的关系
定义BPMN事件的 :code:`Task`：一个 :code:`TaskSpec` 具有额外的 :code:`event_definition` 属性，该属性包含有关将被捕获或引发的事件的信息。

当抛出事件时，将使用与任务的规范和有效负载（如果适用）关联的 :code:`EventDefinition` 创建 :code:`BpmnEvent` 。
对于具有有效载荷的事件，:code:`EventDefinition` 将定义如何基于工作流实例创建有效载荷，并将其包含在事件中。
Timer Event将知道如何解析和计算所提供的表达式, 等等。

事件将传递给 :code:`workflow.catch` 方法，该方法将迭代所有任务，并将事件传递给等待该事件的任何任务。
如果工作流中没有捕获事件的任务，则事件将被放置在挂起的事件队列中，并且可以使用 :code:`workflow.get_events` 方法检索这些事件。

.. note::

    此方法会清除事件队列，因此，如果您的应用程序检索到事件而不处理它，那么它将永远消失！

此repo中的应用程序设计为运行单个工作流，因此没有任何外部事件处理。
如果您实现了这样的功能，您将需要一种方法来确定任何检索到的事件应该发送到哪个进程。

:code:`workflow.waiting_events` 将返回一个 :code:`PendingBpmnEvents` 列表，该列表包含事件的名称和类型，可用于帮助确定这一点。

一旦您确定了哪个工作流应该接收事件，就可以将其传递给 :code:`workflow.catch` 来处理它。

