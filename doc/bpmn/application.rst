概述
========

本节重点介绍示例应用程序，而不是库本身；它旨在引导人们尝试使用此文档，因此我们不会在其中投入太多空间（其中大部分是一个正常运行的应用程序所必需的，但与库的使用无关）；尽管如此，还是有相当多的代码，对这里的内容有一个大致的了解会有所帮助。

该应用程序包括几个部分：

- 一个引擎，它使用SpiffWorkflow来运行、解析和序列化工作流
- 用于运行和检查工作流的curses UI，该UI使用引擎
- 具有一些有限功能的命令行UI，它也使用引擎

我们将主要关注引擎，因为它包含与库的接口，尽管其他组件会提供一些示例。与处理用户输入和在终端中显示信息所需的代码相比，该引擎相当小且简单。
配置是在python模块中设置的，并使用“-e”参数传递到应用程序中，该参数从该文件加载配置的引擎。这种设置应该使其相对改变发动机的行为。包括以下配置：

- :code:`spiff_example.spiff.file`: 使用spiff BPMN扩展并序列化为JSON文件
- :code:`spiff_example.spiff.sqlite`: 使用spiff BPMN扩展并序列化到SQLite
- :code:`spiff_example.camunda.default`: 使用Camunda扩展并序列化到SQLite

.. _quickstart:

快速启动
==========

产品订购过程有几个版本，其复杂性各不相同，位于
:example:`bpmn/tutorial` repo的目录，其中包含SpiffWorkflow支持的大多数元素。这些图表可以在任何BPMN编辑器中查看，但其中许多都有使用创建的自定义扩展
`bpmn-js-spiffworflow <https://github.com/sartography/bpmn-js-spiffworkflow>`_.

要通过命令行添加工作流并将序列化规范存储在JSON文件中，请执行以下操作：

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file add \
      -p order_product \
      -b bpmn/tutorial/{top_level,call_activity}.bpmn \
      -d bpmn/tutorial/{product_prices,shipping_costs}.dmn

要使用序列化的JSON文件运行curses应用程序，请执行以下操作：

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file

选择“启动工作流”屏幕并启动流程。

略深入的应用
======================================

应用程序需要加载的模块的名称，该模块包含如上定义的配置之一。

要使用JSON文件序列化程序启动curses UI，请执行以下操作：

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file

如果应用程序在没有其他参数的情况下运行，则会加载curses UI。

可以通过curses UI添加工作流规范，但这样做会有点痛苦，除非你是一个比我更好的打字员和校对员；因此，还有一些命令行实用程序用于处理一些功能，包括添加工作流规范。

命令行选项包括

- :code:`add` 添加工作流规范（同时利用shell的文件完成功能）
- :code:`list` 列出可用的规格
- :code:`run` 以非交互方式运行工作流

每个选项都有一个帮助菜单，介绍如何使用它们。

配置模块
=====================

用户可以自定义库的三种主要方式是：

-解析器
-脚本引擎
-序列化程序

我们使用配置模块来允许这些组件在工作流引擎本身之外定义并传递作为参数，使实验更容易。我经常被问到为什么图表没有按预期执行，或者如何使脚本引擎以特定方式工作；这是第一次设置
对我来说，这比配置库的测试加载程序并在调试器中运行它更有效；我希望其他人也会发现它很有用。

我们将在后面的章节中更详细地介绍配置，但我们将简要介绍最简单的配置，:app:`spiff/file.py` here.

在这个文件中，我们将初始化我们的解析器：

.. code-block:: python

    parser = SpiffBpmnParser()

我们不需要进一步自定义这个解析器——这是一个内置的解析器，可以处理DMN文件以及SpiffBPMN扩展

我们还需要初始化一个序列化程序：

.. code-block:: python

    dirname = 'wfdata'
    FileSerializer.initialize(dirname)
    registry = FileSerializer.configure(SPIFF_CONFIG)
    serializer = FileSerializer(dirname, registry=registry)

JSON规范和工作流将存储在 :code:`wfdata`.  这个 :code:`registry` 是维护有关将Python对象转换为JSON可序列化字典形式以及从JSON可序列化词典形式转换Python对象的信息的地方。 :code:`SPIFF_CONFIG` 告诉序列化程序如何处理Spiff内部使用的对象。工作流也可以包含任意数据，因此此注册表还可以告诉序列化程序如何处理工作流中的任何不可序列化数据。我们将在中详细介绍 :ref:`serializing_custom_objects`.

我们初始化脚本环境：

.. code-block:: python

    script_env = TaskDataEnvironment({'datetime': datetime })
    >script_engine = PythonScriptEngine(script_env)

这个 :code:`PythonScriptEngine`处理脚本任务的执行以及网关和DMN条件的评估。
我们将在此基础上创建脚本引擎；执行和评估将在这种环境的背景下进行。

SpiffWorkflow提供了一个默认的脚本环境，适用于简单的应用程序，但应用程序可能需要以某种方式扩展（或限制）它。 看 :doc:`script_engine` 示例。因此，我们有能力选择性地传入一个。

在这种情况下，我们将包括对 :code:`datetime` 模块，因为我们将在几个脚本任务中使用它。

我们还指定了一些处理程序：

.. code-block:: python

    handlers = {
        UserTask: UserTaskHandler,
        ManualTask: ManualTaskHandler,
        NoneTask: ManualTaskHandler,
    }

这是任务规范到任务处理程序的映射，让我们的应用程序知道如何处理这些任务。

.. note::

    在我们的应用程序中，我们还传递了处理程序，但这不是一个典型的用例。该库知道如何处理除人工（用户和手动）任务之外的所有任务类型，这些处理程序通常会内置到您的应用程序中。然而，这个应用程序需要能够处理多组人工任务规范，这是一种方便的方法。默认情况下，库将“无”任务（未指定特定类型的任务）视为“手动任务”。

然后，我们使用以下每个组件创建BPMN引擎(:app:`engine/engine.py`)：

.. code-block:: python

    from ..engine import BpmnEngine
    engine = BpmnEngine(parser, serializer, handlers, script_env)

