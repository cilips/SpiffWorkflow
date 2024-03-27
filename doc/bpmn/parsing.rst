分析BPMN
============

示例应用程序假设 :code:`BpmnProcessSpec` 将独立于启动工作流为每个进程生成，并且这些进程将立即序列化并提供ID。
我们稍后将更详细地讨论序列化；现在我们只需注意，文件序列化程序只需将规范的JSON表示写入文件，并使用文件名作为ID。

.. note::

    这是一种设计选择——每次运行流程时都可以重新解析规范。

默认分析器
===============

Importing
---------

每个BPMN模块 (:code:`bpmn`, :code:`spiff`, or :code:`camunda`) 具有用该模块中的规范预配置的解析器（如果特定的TaskSpec没有在该模块中实现，:code:`bpmn` TaskSpec is used).

- :code:`bpmn`: :code:`from SpiffWorkflow.bpmn.parser import BpmnParser`
- :code:`dmn`: :code:`from SpiffWorkflow.dmn.parser import BpmnDmnParser`
- :code:`spiff`: :code:`from SpiffWorkflow.spiff.parser import SpiffBpmnParser`
- :code:`camunda`: :code:`from SpiffWorkflow.camunda.parser import CamundaParser`

.. note::

   默认解析程序无法解析DMN文件。这个:code:`BpmnDmnParser` 扩展默认解析器以添加该功能。两者 :code:`spiff` and :code:`camunda` 解析器继承自 :code:`BpmnDmnParser`.

解析器的实例化没有必需的参数，但有几个可选参数。

Validation
----------

这个 :code:`SpiffWorkflow.bpmn.parser` 模块还包含 :code:`BpmnValidator`.

默认验证器根据BPMN 2.0规范进行验证。还可以导入其他规范（例如，用于自定义扩展）。

默认情况下，解析器不进行验证，但如果传入了验证器，它将用于添加到解析器的任何文件

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import BpmnParser, BpmnValidator
    parser = BpmnParser(validator=BpmnValidator())

规格说明
-----------------

默认设置 :code:`decription` 每个任务规范的属性。该描述旨在以用户友好的方式表示任务类型。它是XML标记到字符串的映射。

默认的描述集可以在中找到 :code:`SpiffWorkflow.bpmn.parser.spec_descriptions`.

从BPMN流程创建BpmnProcessSpec
--------------------------------------------

从这个 :code:`add_spec` BPMN引擎的方法 (:app:`engine/engine.py`):

.. code-block:: python

    def add_spec(self, process_id, bpmn_files, dmn_files):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec = self.parser.get_spec(process_id)
            dependencies = self.parser.get_subprocess_specs(process_id)
        except ValidationException as exc:
            self.parser.process_parsers = {}
            raise exc
        spec_id = self.serializer.create_workflow_spec(spec, dependencies)
        logger.info(f'Added {process_id} with id {spec_id}')
        return spec_id

    def add_files(self, bpmn_files, dmn_files):
        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files is not None:
            self.parser.add_dmn_files(dmn_files)

第一步是使用 :code:`add_bpmn_files` 和 :code:`add_dmn_files` 方法.

我们使用 :code:`get_spec` 使用提供的解析BPMN流程 :code:`process_id` (*not* 进程名称).

.. note::

    该解析器被设计为加载一组文件并解析一个进程，并将引发一个 :code:`ValidationException`
   如果存在任何重复的ID。可用的进程会立即添加到 :code:`process_parsers`, 因此，重新添加文件将生成一个异常。因此，如果我们遇到问题（这里的具体情况）或希望重用同一个解析器，我们需要清除此属性。

添加文件的其他方法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :code:`add_bpmn_files_by_glob`: Loads files from a glob instead of a list.
- :code:`add_bpmn_file`: Adds one file rather than a list.
- :code:`load_bpmn_str`: Loads and parses XML from a string.
- :code:`load_bpmn_io`: Loads and parses XML from an object implementing the IO interface.
- :code:`load_bpmn_xml`: Parses BPMN from an :code:`lxml` parsed tree.

.. _parsing_subprocesses:

处理子流程和调用活动
-----------------------------------------

在内部，调用活动和子流程（以及事务子流程）都被视为单独的规范。这是为了防止单个规范变得太大，尤其是在同一个过程规范将被多次调用的情况下。

这个 :code:`get_subprocess_specs` 方法获取进程ID，并递归地搜索由所提供的BPMN文件使用或定义的调用活动、子进程等。它返回进程ID到已解析规范的映射。

查找依赖项的其他方法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- :code:`find_all_specs`: 返回名称的映射 -> :code:`BpmnWorkflowSpec` 用于所有文件中的所有进程，这些文件当时已提供给解析器。
- :code:`get_process_dependencies`: 返回提供的进程ID所引用的进程ID的列表
- :code:`get_dmn_dependencies`: 返回提供的进程ID引用的DMN ID的列表

从BPMN协作创建BpmnProcessSpec
----------------------------------------------------

解析器还可以基于协作生成工作流规范：

.. code-block:: python

    def add_collaboration(self, collaboration_id, bpmn_files, dmn_files=None):
        self.add_files(bpmn_files, dmn_files)
        try:
            spec, dependencies = self.parser.get_collaboration(collaboration_id)
        except ValidationException as exc:
            self.parser.process_parsers = {}
            raise exc

为协作中的每个流程创建一个规范，并且这些流程中的每个都封装在一个子工作流中。这意味着以这种方式创建的规范将始终需要子流程规范，并且此方法返回生成的规范（与BPMN文件中的任何内容都不直接对应）以及文件中存在的流程和利润依赖关系。

