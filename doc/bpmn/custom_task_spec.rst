实现自定义任务规范
-------------------------------

假设我们想在SpiffWorkflow之外管理计时器启动事件。如果我们加载并运行了一个进程，该进程以计时器开始，则计时器将等待事件发生；这可能需要几天或几周后。

当然，我们总是可以检查它是否在等待并序列化工作流，直到那个时候。然而，我们可能会决定，我们根本不希望SpiffWorkflow来管理这一点。我们可以使用自定义任务规范来完成此操作。

首先，我们将创建一个新类

.. code:: python

    from SpiffWorkflow.bpmn.specs.event_definitions import NoneEventDefinition
    from SpiffWorkflow.bpmn.specs.event_definitions.timer import TimerEventDefinition
    from SpiffWorkflow.bpmn.specs.mixins import StartEventMixin
    from SpiffWorkflow.spiff.specs import SpiffBpmnTask

    class CustomStartEvent(StartEventMixin, SpiffBpmnTask):

        def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):

            if isinstance(event_definition, TimerEventDefinition):
                super().__init__(wf_spec, bpmn_id, NoneEventDefinition(), **kwargs)
                self.timer_event = event_definition
            else:
                super().__init__(wf_spec, bpmn_id, event_definition, **kwargs)
                self.timer_event = None

当我们创建自定义事件时，我们将检查是否使用 :code:`TimerEventDefinition`, 如果是，我们将用 :code:`NoneEventDefinition`.
有三种不同类型的Timer Events，因此我们将使用这三种类型的基类来确保我们考虑TimeDate、Duration和Cycle。

.. note::

    我们的类继承自两个类。我们导入一个mixin类，该类定义了来自
    :code:`StartEventMixin` 在 :code:`bpmn` 包及 :code:`SpiffBpmnTask` 来自 :code:`spiff` 包, 它扩展了默认值 :code:`BpmnSpecMixin`.

    我们将特定BPMN任务的基本行为从 :code:`BpmnSpecMixin` 以便在不遇到MRO问题的情况下更容易地扩展它们。

    通常，如果实现自定义任务规范，则需要从这两个类别的基础继承。

每当我们创建自定义任务规范时，我们都需要为其创建一个转换器，以便对其进行序列化。

.. code:: python

    from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
    from SpiffWorkflow.bpmn.serializer.default import EventConverter
    from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

    class CustomStartEventConverter(SpiffBpmnTaskConverter):

        def __init__(self, registry):
            super().__init__(CustomStartEvent, registry)

        def to_dict(self, spec):
            dct = super().to_dict(spec)
            if spec.timer_event is not None:
                dct['event_definition'] = self.registry.convert(spec.timer_event)
            else:
                dct['event_definition'] = self.registry.convert(spec.event_definition)
            return dct


    DEFAULT_CONFIG['task_specs'].remove(StartEventConverter)
    DEFAULT_CONFIG['task_specs'].append(CustomStartEventConverter)
    registry = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)
    serializer = BpmnWorkflowSerializer(registry)

我们的转换器将继承自 :code:`SpiffBpmnTaskConverter`, 因为这是我们的基本通用BPMN mixin类。

这个 :code:`SpiffBpmnTaskConverter` 本身继承自
:code:`SpiffWorkflow.bpmn.serializer.helpers.task_spec.BpmnTaskSpecConverter`。 其提供了一些用于从任务中提取标准属性的辅助方法；
the :code:`SpiffBpmnTaskConverter` 对的扩展执行相同操作来自 :code:`spiff` 包。

我们不需要做太多——我们所做的只是用原始定义替换事件定义。当任务恢复时，计时器事件将被移动，这使我们不必编写自定义解析器。

.. note::

    最好让类的init方法同时使用事件定义和计时器事件定义。不幸的是，我们的解析器不是很直观，也不容易扩展，所以我这样做是为了让它更容易理解。

当我们创建序列化程序时，我们需要告诉它这个任务。我们将删除标准启动事件的转换器，并将我们创建的转换器添加到配置中。
然后，我们获得序列化程序所知道的类的注册表，其中包括我们的自定义规范以及所有其他规范，并用它初始化序列化程序。

.. note::

    之所以需要两个步骤（重新调用注册表并然后将其传递给序列化程序），而不是直接使用配置，是为了允许对 :code:`registry`.
    工作流可以包含artrary数据，我们希望为开发人员提供序列化任何对象的代码的能力。 查看
    :ref:`serializing_custom_objects` 有关如何工作的更多信息。

最后，我们必须更新我们的解析器：

.. code:: python

    from SpiffWorkflow.spiff.parser import SpiffBpmnParser
    from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
    from SpiffWorkflow.bpmn.parser.util import full_tag

    parser = SpiffBpmnParser()
    parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)

解析器包含类属性，这些属性定义了如何解析特定元素以及应用于创建任务规范的类，因此，我们不将这些作为参数传入，而是创建一个解析器，然后更新它将使用的值。
这有点不直观，但它就是这样工作的。

幸运的是，我们能够重用现有的任务规范解析器，这大大简化了过程。

在创建了解析器和序列化程序之后，我们可以创建一个配置模块并用这些组件实例化引擎。

有一个非常简单的图表 :bpmn:`timer_start.bpmn` 具有进程ID `timer_start` 带有一个持续时间计时器为一天的开始事件，可用于说明自定义任务的工作方式。
如果使用提供的任何配置运行此工作流，您将看到 `WAITING` 开始事件; 如果您使用我们刚刚创建的解析器和序列化程序，您将被建议立即完成用户任务。
