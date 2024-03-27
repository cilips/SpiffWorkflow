SpiffWorkflow的基本概念
==================================

概述
--------

这个库的目的是提供一个通用的工作流执行环境，其中包含各种各样的内置任务，支持许多不同工作流模式的类型。

SpiffWorkflow 跟踪任务依赖关系和状态，并提供序列化或反序列化尚未完成的工作流。使用此库的开发人员可以专注于显示工作流的状态和
向其应用程序的用户呈现其任务。

.. _specs_vs_instances:

规范与实例
----------------------------

SpiffWorkflow 由两类不同的对象组成：

- **Specification 对象**, 其表示结构和行为的定义，并源自 :code:`WorkflowSpec` and :code:`TaskSpec`
- **Instance 对象**, 表示正在运行的工作流的状态 (:code:`Workflow`/:code:`BpmnWorkflow` and :code:`Task`)

在工作流上下文中，规范是工作流的模型，它描述了每当执行工作流时可以采用的每一条路径。实例是规范的特定实例化。它描述了当前状态或工作流运行时实际采用的路径

在任务上下文中，规范是任务行为的模型。它描述了决定运行相关任务是否存在先决条件的机制，如何决定是否满足这些先决条件，以及完成（成功或失败）意味着什么。实例描述任务的状态，因为它属于特定的工作流，并包含用于管理该状态的数据。
规范是唯一的，而实例则不是。工作流有一个模型，特定任务有一个规范。
想象一个有循环的工作流。循环在规范中定义一次，但可能有许多任务与构成循环的每个规范相关。

在 BPMN 示例 (:ref:`quickstart`), 我们描述了商品选择过程:

    开始 -> 选择和定制商品 -> 继续购物?

由于客户可能会选择多个产品，因此我们的实例外观取决于客户的操作。如果他们选择三种产品，然后我们得到以下路径::

    开始 --> 选择和定制商品 -> 继续购物? -> |
          /-------------------------------------------------------- /
          |-> 继续购物 -> 继续购物? -> |
          /-------------------------------------------------------- /
          |-> 继续购物 -> 继续购物?

有*一个*TaskSpec描述产品选择和定制，*一个*TaskSpec决定是否添加更多项，但它可以执行任意次数，从而导致这些TaskSpec的任务数量与客户选择产品数量一样多
。

一个任务规范可能有多个输入（如果有多条路径可以到达它），但一个任务只有一个父级。规范可能包含循环，但实例化的工作流始终是一棵树。

.. _states:

了解任务状态
-------------------------

* **PREDICTED** 任务

 预测任务是指可能但不一定在未来某个时间运行的任务。例如，如果任务遵循条件网关，那么在到达网关并评估条件之前，将不知道采用哪条路径。有两种类型的预测任务:

  - **MAYBE**: 任务是条件路径的一部分
  - **LIKELY** : 任务是条件路径上的默认输出

* **DEFINITE** 任务

  随着工作流程的进展，确定的任务肯定会运行

  - **FUTURE**: 任务肯定会运行。
  - **WAITING**: 在任务变为就绪之前，必须满足一个条件
  - **READY**: 已满足运行此任务的先决条件
  - **STARTED**: 任务已开始运行，但尚未完成

* **FINISHED** 任务

  已完成的任务是指不再采取进一步行动的任务。

  - **COMPLETED**: 任务已成功完成。
  - **ERROR**: 任务未成功完成。
  - **CANCELLED**: 任务在运行前或运行中被取消。

Tasks start in either a **PREDICTED** or **FUTURE** state, move through one or more **DEFINITE** states, and end in a
**FINISHED** state.  State changes are determined by task spec methods.

钩子
-----

SpiffWorkflow executes a Task by calling a series of hooks that are tightly coupled
to Task State. These hooks are:

* `_update_hook`: This method will be run by a task's predecessor when the predecessor completes.  The method checks the
  preconditions for running the task and returns a boolean indicating whether a task should become **READY**.  Otherwise,
  the state will be set to **WAITING**.

* `_on_ready_hook`: This method will be run when the task becomes **READY** (but before it runs).

* `run_hook`: This method implements the task's behavior when it is run, returning:

  - :code:`True` if the task completed successfully.  The state will transition to **COMPLETED**.
  - :code:`False` if the task completed unsucessfully.  The state will transition to **ERRROR**.
  - :code:`None` if the task has not completed.  The state will transition to **STARTED**.

* `_on_complete_hook`: This method will be run when the task's state is changed to **COMPLETED**.

* `_on_error_hook`: This method will be run when the task's state is changed to **ERROR**.

* `_on_trigger`: This method executes the task's behavior when it is triggered (`Trigger` tasks only).

Task Prediction
---------------

Each TaskSpec also has a `_predict_hook` method, which is used to set the state of not-yet-executed children.  The behavior
of `_predict_hook` varies by TaskSpec.  This is the mechanism that determines whether Tasks are **FUTURE**, **LIKELY**, or
**MAYBE**.  When a workflow is created, a task tree is generated that contains all definite paths, and branches of
**PREDICTED** tasks with a maximum length of two.  If a **PREDICTED** task becomes **DEFINITE**, the Task's descendants
are re-predicted.  If it's determined that a **PREDICTED** will not run, the task and all its descendants will be dropped
from the tree.  By default `_on_predict_hook` will ignore **DEFINITE** tasks, but this can be overridden by providing a
mask of `TaskState` values that specifies states other than **PREDICTED**.

Where Data is Stored
--------------------

Data can ba associated with worklows in the following ways:

- **Workflow data** is stored on the Workflow, with changes affecting all Tasks.
- **Task data** is local to the Task, initialized from the data of the Task's parent.
- **Task internal data** is local to the Task and not passed to the Task's children
- **Task spec data** is stored in the TaskSpec object, and if updated, the updates will apply to any Task that references the spec
  (unused by the :code:`bpmn` package and derivatives).

