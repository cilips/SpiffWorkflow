教程-非BPMN
===================

介绍
------------

在本章中，我们将使用Spiff工作流来解决现实世界中的一个问题：我们将创建一个触发核打击的工作流。

我们假设您熟悉 :doc:`../../concepts`.

假设你想发射火箭，但前提是总统和将军都签字同意。

定义工作流有两种不同的方式：要么通过反序列化（来自XML或JSON），或使用Python。

创建工作流规范（使用Python）
--------------------------------------------------

作为第一步，我们将用代码创建一个简单的工作流。
在Python中，工作流定义如下：

.. literalinclude:: nuclear.py

希望代码是自我解释的。
使用Python编写工作流很快就会变得乏味。通常最好使用另一种格式。

创建工作流规范（使用JSON）
----------------------------------------------

一旦完成了如上所示的序列化程序，就可以用JSON编写规范。

以下是一个与上面的Python WorkflowSpec完全相同的示例：

.. literalinclude:: nuclear.json

创建不符合规范的工作流
--------------------------------------------

现在是时候开始并根据规范实际创建和执行工作流了。

由于我们在规范中包含了*manual*任务，您将希望在实践中实现用户界面，但我们只是假设本教程中的所有任务都是自动的。
请注意，*manual*标志对控制流程没有影响；它只是用户界面可以用来识别需要用户输入的任务的标志。

.. literalinclude:: start.py

:meth:`SpiffWorkflow.Workflow.complete_all` 根据规范完成所有任务，直到没有其他任务可供执行。
请注意，这并不意味着工作流是在调用:meth:`SpiffWorkflow.Workflow.complete_all`，
因为例如，某些任务可能正在等待，或者可能被另一个等待任务阻止。


序列化工作流
----------------------

如果要存储 :class:`SpiffWorkflow.specs.WorkflowSpec`, 您可以用 :meth:`SpiffWorkflow.specs.WorkflowSpec.serialize`:

.. literalinclude:: serialize.py

如果要存储 :class:`SpiffWorkflow.Workflow`, 您可以用 :meth:`SpiffWorkflow.Workflow.serialize`:

.. literalinclude:: serialize-wf.py

反序列化工作流
------------------------

以下示例显示如何恢复
:class:`SpiffWorkflow.specs.WorkflowSpec` 使用
:meth:`SpiffWorkflow.specs.WorkflowSpec.serialize`.

.. literalinclude:: deserialize.py

恢复:class:`SpiffWorkflow.Workflow`, 使用
:meth:`SpiffWorkflow.Workflow.serialize` 代替:

.. literalinclude:: deserialize-wf.py

从这里去哪里？
----------------------

第一个教程实际上有一个问题：如果你想保存工作流，SpiffWorkflow将无法重新连接信号，因为它无法保存对代码的引用。

因此，在反序列化工作流之后，您将需要自己重新连接信号。

如果你想让SpiffWorkflow为你处理这个问题，你需要创建一个自定义任务，并告诉Spiff工作流如何序列化和反序列化它。
下一个教程将展示如何做到这一点。
