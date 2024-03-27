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

In the workflow context, a specification is model of the workflow, an abstraction that describes *every path that could
be taken whenever the workflow is executed*.  An instance is a particular instantiation of a specification.  It describes *the
current state* or *the path(s) that were actually taken when the workflow ran*.

In the task context, a specification is a model for how a task behaves.  It describes the mechanisms for deciding *whether
there are preconditions for running an associated task*, *how to decide whether they are met*, and *what it means to complete
(successfully or unsuccessfully)*.  An instance describes the *state of the task, as it pertains to a particular workflow* and
*contains the data used to manage that state*.

Specifications are unique, whereas instances are not.  There is *one* model of a workflow, and *one* specification for a particular task.

Imagine a workflow with a loop.  The loop is defined once in the specification, but there can be many tasks associated with
each of the specs that comprise the loop.

In our BPMN example (:ref:`quickstart`), we described a product selection process:

    Start -> Select and Customize Product -> Continue Shopping?

Since the customer can potentially select more than one product, how our instance looks depends on the customer's actions.  If
they choose three products, then we get the following path::

    Start --> Select and Customize Product -> Continue Shopping? -> |
          /-------------------------------------------------------- /
          |-> Select and Customize Product -> Continue Shopping? -> |
          /-------------------------------------------------------- /
          |-> Select and Customize Product -> Continue Shopping?

There is *one* TaskSpec describing product selection and customization and *one* TaskSpec that determines whether to add more
items, but it may execute any number of times, resulting in as many Tasks for these TaskSpecs as the number of products the
customer selects.

A Task Spec may have multiple inputs (if there are multiple paths to reach it) but a Task has only one parent.  A specification
may contains cycles, but an instantiated workflow is *always* a tree.

.. _states:

Understanding Task States
-------------------------

* **PREDICTED** Tasks

  A predicted task is one that will possibly, but not necessarily run at a future time.  For example, if a task follows a
  conditional gateway, which path is taken won't be known until the gateway is reached and the conditions evaluated.  There
  are two types of predicted tasks:

  - **MAYBE**: The task is part of a conditional path
  - **LIKELY** : The task is the default output on a conditional path

* **DEFINITE** Tasks

  Definite tasks are certain to run as the workflow progresses.

  - **FUTURE**: The task will definitely run.
  - **WAITING**: A condition must be met before the task can become **READY**
  - **READY**: The preconditions for running this task have been met
  - **STARTED**: The task has started running but has not finished

* **FINISHED** Tasks

  A finished task is one where no further action will be taken.

  - **COMPLETED**: The task finished successfully.
  - **ERROR**: The task finished unsucessfully.
  - **CANCELLED**: The task was cancelled before it ran or while it was running.

Tasks start in either a **PREDICTED** or **FUTURE** state, move through one or more **DEFINITE** states, and end in a
**FINISHED** state.  State changes are determined by task spec methods.

Hooks
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

