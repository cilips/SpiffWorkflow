SpiffWorkflow异常
========================

有关SpiffWorkflow中异常和异常层次结构的详细信息

SpiffWorkflow异常
----------------------
SpiffWorkflow引发的所有异常的基本异常

验证异常
-------------------

**继承**
SpiffWorkflowException

在分析工作流时抛出。

**属性/方法**

- **tag**:  正在分析的xml标记的类型
- **id**:  xml标记的id属性（如果可用）。
- **name**:  xml标记的name属性（如果可用）。
- **line_number**:  出现标记的行号。
- **file_name**: 发生错误的文件的名称。
- **message**:  人类可读的错误消息。


工作流异常
-----------------
当任务规范发生错误时（可能应该称为SpecException）

**继承**
SpiffWorkflowException

**属性/方法**

- **task_spec**:  TaskSpec-导致错误发生的特定任务、网关等。
- **error**:  描述问题的人工可读错误消息。


工作流数据异常
---------------------
发生异常时，在任务和数据对象之间移动数据（包括数据输入和数据输出）

**继承**
WorkflowException

**属性/方法**

（除了WorkflowException中的值之外）

 - **task**:  具体任务（不是任务规范，而是实际执行的任务）
 - **data_input**: 输入变量的规范
 - **data_output**: 输出变量的规格

WorkflowTaskException
---------------------
**继承**
WorkflowException

它将接受line_number和error_line作为参数-如果提供的基本错误是SyntaxError，它将尝试从错误中派生此信息。
如果这是一个名称错误，它将尝试计算一个你是说error_msg吗。

**属性/方法**

（除了WorkflowException中的值之外）

 - **task**:  具体任务（不是任务规范，而是实际执行的任务）
 - **error_msg**: 详细的人类可读信息。（与上述错误冲突）
 - **exception**: 最初的例外情况到此为止。
 - **line_number** 包含错误的行号
 - **offset** 导致错误的线上的点
 - **error_line** 导致错误的行的内容。
 - **get_task_trace**:  提供一个特定的任务，将通过工作流/子流程和调用活动来显示错误发生的位置。
如果错误发生在深度嵌套的结构中（其中调用活动包括调用活动…），则非常有用
 - **did_you_mean_name_error**: 将丢失的数据值与数据的内容进行比较

