模块
=======

SpiffWorkflow 由几个模块组成。该包中包含的模块及其结构都是历史性原因的。
该库最初只包含核心库规范，它后来被扩展为提供 BPMN 支持（在某种程度上不完全符合原始库的运作），然后 BPMN 支持被进一步细化为 BPMN规范的自定义扩展提供支持。
最近的重新开发主要集中在 BPMN 上对核心库的更改。因此，BPMN 和非 BPMN 部分之间存在相当显著的差异,我们正在努力使这些库保持一致！

核心库
----------------

核心库提供了大量任务规范类型和基本工作流执行功能的基本实现。

- 规范实现在 :code:`specs`
- 工作流工作流 :code:`workflow.py`
- 任务工作流 :code:`task.py`, 具有用于进行迭代和筛选的实用程序在 :code:`util.task.py`

它记录在 :doc:`core/index` 。

通用BPMN实现
---------------------------

该模块扩展了核心库实现，以支持 BPMN 图的解析和执行。

:code:`bpmn.specs` 扩展了核心库的基本规范，以实现中的通用 BPMN 属性和行为, 任务规范以两种方式扩展：
为所有BPMN任务提供通用行为 (:code:`bpmn.specs.mixins.bpmn_spec_mixin.BpmnSpecMixin`) 和特定类型的行为 (:code:`bpmn.specs.mixins`)。
允许任意一类属性分别扩展。

- BPMN 包中的工作流实现以与核心库采用完全不同的方式处理子工作流。它反序列化程序已被完全替换。允许对具有特定 BPMN 属性的任务进行筛选和迭代。
- 工作流有一个脚本环境，将在其中执行特定任务的代码（在核心库中，这将通过产生子流程的执行任务或自定义任务规范来完成）。
- 序列化程序已被完全替换。

该模块记录在 :doc:`bpmn/index` 。

Spiff BPMN扩展
---------------------

此模块扩展了通用BPMN实现，支持使用自定义的扩展
`Spiff Arena <https://spiff-arena.readthedocs.io/en/latest/>`_ 。

Camunda BPMN扩展
-----------------------

此模块扩展了通用BPMN实现，对Camunda扩展的支持有限。

.. warning::

    Camunda一揽子计划尚未开发中。我们将接受Camunda用户的贡献，但我们不会积极维护此包。
