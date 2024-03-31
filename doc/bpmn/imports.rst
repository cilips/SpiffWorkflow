创建和运行工作流
==============================

.. code-block:: python

    from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
    from SpiffWorfkflow import TaskState

解析
=======

基本解析
-------------

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import BpmnParser, BpmnValidator

自定义解析
------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import TaskParser, EventDefinitionParser

示例
--------

- :doc:`parsing`
- :doc:`custom_task_spec`

脚本引擎
=============

修改默认执行环境
-------------------------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

控制引擎与工作流的交互方式
-----------------------------------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine

实现自定义exec/eval
-----------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import BasePythonScriptEngineEnvironment

示例
--------

- :doc:`script_engine`

规格
=====

使用规格
------------

.. code-block:: python

    from SpiffWorkflow.bpmn.specs import <TaskSpec>
    from SpiffWorkflow.bpmn.specs.event_definition import <EventDefinition>

扩展规格
----------------

.. code-block:: python

    from SpiffWorkflow.bpmn.specs import BpmnTaskSpec           # Implements generic BPMN behavior
    from SpiffWorkflow.bpmn.specs.mixins import <TaskSpecMixin> # Implements specific BPMN behavior

实现数据存储
---------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.spec import BpmnDataStoreSpecification

示例
--------

- :doc:`workflows`
- :doc:`custom_task_spec`

序列化程序
==========

基本用法
-----------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

自定义数据
-----------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import DefaultRegistry

规格自定义
-------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import DEFAULT_CONFIG
    from SpiffWorkflow.bpmn.serializer.default import <TaskSpecConverter>
    from SpiffWorkflow.bpmn.serializer.helpers import (
        TaskSpecConverter,
        EventDefinitionConverter,
        BpmnDataSpecificationConverter,
    )

示例
--------

- :doc:`serialization`
- :doc:`custom_task_specs`

DMN
===

.. code-block:: python

    from SpiffWorkflow.dmn.parser import BpmnDmnParser
    from SpiffWorkflow.dmn.specs import BusinessRuleTaskMixin
    from SpiffWorkflow.dmn.serializer import BaseBusinessRuleTaskConverter

Spiff
=====

.. code-block:: python

    from SpiffWorkflow.spiff.parser import SpiffBpmnParser, VALIDATOR
    from SpiffWorkflow.spiff.specs import <TaskSpec>
    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

Camunda
=======

.. code-block:: python

    from SpiffWorkflow.camunda.parser import CamundaParser
    from SpiffWorkflow.camunda.specs import <TaskSpec>
    from SpiffWorkfllw.camunda.serializer import DEFAULT_CONFIG

