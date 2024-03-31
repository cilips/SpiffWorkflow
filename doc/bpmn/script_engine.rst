脚本引擎概述
======================

您可能需要修改默认脚本引擎，无论是因为您需要为其提供额外的功能，还是因为出于安全原因，您可能希望限制其功能。

.. warning::

   默认情况下，脚本环境将输入直接传递给 :code:`eval` 及 :code:`exec`!  在大多数情况下，您需要将默认的脚本环境替换为自己的脚本环境。

限制脚本环境
==================================

以下示例将默认全局环境替换为
`RestrictedPython <https://restrictedpython.readthedocs.io/en/latest/>`_

我们已经修改了引擎配置，以便在中使用受限制的环境 :app:`spiff/restricted.py`

.. code:: python

    from RestrictedPython import safe_globals
    from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

    restricted_env = TaskDataEnvironment(safe_globals)
    restricted_script_engine = PythonScriptEngine(environment=restricted_env)

我们还包括了一个危险的过程 :bpmn:`dangerous.bpmn`

如果您使用常规脚本environment运行此进程，BPMN进程将获得操作系统进程ID并提示您终止它；
如果你回答“是”，它会这么做（它实际上不会做比搞砸你的终端设置更危险的事情，但希望能证明这一点）。

.. code-block:: console

    ./runner.py -e spiff_example.spiff.file add -p end_it_all -b bpmn/tutorial/dangerous.bpmn
    ./runner.py -e spiff_example.spiff.file

如果加载受限制的引擎：

.. code-block:: console

    ./runner.py -e spiff_example.spiff.restricted

你会得到一个错误，因为导入受到限制。

.. note::

    由于我们使用了完全相同的解析器和序列化程序，因此我们可以简单地在它们之间来回切换两个脚本引擎（这是两种配置之间的唯一区别）。

使自定义类和函数可用
=============================================

您可能想要自定义脚本环境的另一个原因是提供对自定义脚本的访问类或函数。

在我们的许多示例模型中，我们使用DMN表来获取产品信息。DMN是一个方便的使表格数据可用于我们的流程的方式。

然而，在一个稍微现实一点的场景中，我们肯定会有关于如何在某个地方的数据库中定制产品的信息。
我们不会在图表中对产品信息进行硬编码（尽管修改BPMN和DMN模型比更改代码本身容易得多！）。
我们的运输成本不会是静态的，而是取决于订单的规模和地点发货——也许我们会查询发货人提供的API。

SpiffWorkflow显然**不会**知道如何查询**您的**数据库或对**您的***供应商进行API调用。
但是，在图中提供此功能的一种方法是在函数中实现调用，并将这些函数添加到脚本环境中，在脚本环境中脚本任务可以调用这些函数。

我们不会实际包含数据库或API，也不会编写用于连接和查询它的代码，但由于我们只有7种产品，
因此我们可以通过简单的字典查找对数据库进行建模，并返回相同的静态信息以供本教程使用。

我们将在中自定义脚本环境 :app:`spiff/custom_object.py`:

.. code:: python

    from collections import namedtuple

    ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])
    INVENTORY = {
        'product_a': ProductInfo(False, False, False, 15.00),
        'product_b': ProductInfo(False, False, False, 15.00),
        'product_c': ProductInfo(True, False, False, 25.00),
        'product_d': ProductInfo(True, True, False, 20.00),
        'product_e': ProductInfo(True, True, True, 25.00),
        'product_f': ProductInfo(True, True, True, 30.00),
        'product_g': ProductInfo(False, False, True, 25.00),
    }

    def lookup_product_info(product_name):
        return INVENTORY[product_name]

    def lookup_shipping_cost(shipping_method):
        return 25.00 if shipping_method == 'Overnight' else 5.00

    script_env = TaskDataEnvironment({
        'datetime': datetime,
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost,
    })
    script_engine = PythonScriptEngine(script_env)

.. note::

    我们还添加了 :code:`datetime`, 因为过程的其他部分需要它。

我们可以像使用任何普通函数一样，在脚本任务中使用自定义函数。要加载使用自定义脚本引擎的示例图，请执行以下操作：

.. code-block:: console

    ./runner.py -e spiff_example.spiff.custom_object add -p order_product \
        -b bpmn/tutorial/{top_level_script,call_activity_script}.bpmn

如果您在交互模式下启动应用程序并选择产品，您将在选择产品后看到任务数据中反映的元组信息。

服务任务
=============

我们也可以使用服务任务来实现相同的目标。服务任务也由工作流的脚本引擎执行，但通过不同的方法，借助中的一些自定义扩展 :code:`spiff` 模块:

- `operation_name`, 分配给被调用服务的名称
- `operation_params`, 操作所需的参数

服务任务的优点是，它比嵌入脚本任务中的函数调用更透明（至少在概念层面上）。

我们执行 :code:`PythonScriptEngine.call_service` 方法在 :app:`spiff/service_task.py`:

.. code:: python

    service_task_env = TaskDataEnvironment({
        'product_info_from_dict': product_info_from_dict,
        'datetime': datetime,
    })

    class ServiceTaskEngine(PythonScriptEngine):

        def __init__(self):
            super().__init__(environment=service_task_env)

        def call_service(self, operation_name, operation_params, task_data):
            if operation_name == 'lookup_product_info':
                product_info = lookup_product_info(operation_params['product_name']['value'])
                result = product_info_to_dict(product_info)
            elif operation_name == 'lookup_shipping_cost':
                result = lookup_shipping_cost(operation_params['shipping_method']['value'])
            else:
                raise Exception("Unknown Service!")
            return json.dumps(result)

    service_task_engine = ServiceTaskEngine()

而不是将我们的自定义功能添加到环境中,我们会重写:code:`call_service` 并根据直接呼叫这个 `operation_name` 已经给出了。
这个 :code:`spiff` Service Task还根据任务数据为我们评估参数，因此我们可以直接传入这些参数。
服务任务还将把我们的结果存储在用户指定的变量中。

我们需要将结果作为json发送回来，因此我们将重用为序列化程序编写的函数 (查看 :ref:`serializing_custom_objects`).

服务任务将分配字典作为操作结果，所以我们将添加一个 `postScript` 到服务任务，
该任务检索创建 :code:`ProductInfo` 实例，所以我们也需要将其添加到脚本环境中。

服务任务的XML如下所示：

.. code:: xml

    <bpmn:serviceTask id="Activity_1ln3xkw" name="Lookup Product Info">
      <bpmn:extensionElements>
        <spiffworkflow:serviceTaskOperator id="lookup_product_info" resultVariable="product_info">
          <spiffworkflow:parameters>
            <spiffworkflow:parameter id="product_name" type="str" value="product_name"/>
          </spiffworkflow:parameters>
        </spiffworkflow:serviceTaskOperator>
        <spiffworkflow:postScript>product_info = product_info_from_dict(product_info)</spiffworkflow:postScript>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_104dmrv</bpmn:incoming>
      <bpmn:outgoing>Flow_06k811b</bpmn:outgoing>
    </bpmn:serviceTask>

将这些信息输入XML有点超出了本教程的范围，因为它不仅仅涉及SpiffWorkflow。
我为这个案例手工编辑了它，但你很难要求你的BPMN作者这么做！

我们的 `modeler <https://github.com/sartography/bpmn-js-spiffworkflow>`_ 具有提供服务及其参数列表的方法，
这些服务及其参数可以在服务任务配置面板中显示给BPMN作者。 中有一个对服务列表进行硬编码的示例
`app.js <https://github.com/sartography/bpmn-js-spiffworkflow/blob/0a9db509a0e85aa7adecc8301d8fbca9db75ac7c/app/app.js#L47>`_
正如所建议的那样，用API调用替换它将是相当简单的。
`SpiffArena <https://www.spiffworkflow.org/posts/articles/get_started/>`_ 具有强大的处理机制，可以作为您的模型。

这一切的工作方式显然在很大程度上取决于您的应用程序，因此我们在此不再赘述，只是为您提供一个自己实现满足自己需求的东西的基本起点。

要运行此工作流，请执行以下操作：

.. code-block:: console

    ./runner.py -e spiff_example.spiff.service_task add -p order_product \
        -b bpmn/tutorial/{top_level_service_task,call_activity_service_task}.bpmn

