实施自定义任务
=========================

介绍
------------

在第二个教程中，我们将实现我们自己的任务，以及使用序列化和反序列化来存储和还原它。

如果你还没有，你应该完成第一个 :doc:`../tutorial/index`。
我们还假设您熟悉：:doc:`../../concepts`。

实施自定义任务
----------------------------

第一步是创建一个 :class:`SpiffWorkflow.specs.TaskSpec` that
fires the rocket::

    from SpiffWorkflow.specs import Simple

    class NuclearStrike(Simple):
        def _on_complete_hook(self, my_task):
            print("Rocket sent!")

将此文件另存为 ``strike.py``.

现在，在我们准备好使用XML或JSON定义工作流之前，我们还必须扩展序列化程序，让SpiffWorkflow知道如何首先表示NuclearStrike。

准备序列化程序
----------------------

在我们可以使用JSON指定工作流之前，我们首先需要教SpiffWorkflow我们的自定义“NuclearChoice”在JSON中是什么样子的。
我们通过扩展

:mod:`SpiffWorkflow.serializer.json.JSONSerializer`.

.. literalinclude:: serializer.py

我们将序列化程序保存为 ``serializer.py``.
我们还需要更新 ``strike.py`` 如下所示：

我们还实现了反序列化程序：

.. literalinclude:: strike.py

仅此而已！现在您已经准备好从JSON创建规范了。

创建工作流规范（使用JSON）
----------------------------------------------

现在我们可以在JSON中的工作流规范中使用NuclearStrike。
请注意，此规范与我们的第一个教程中的规范相同，
只是它参考了我的 `strike.NuclearStrike` 类。

.. literalinclude:: nuclear.json

使用自定义序列化程序和任务
------------------------------------

在这里，我们在实践中使用我们全新的序列化程序：

.. literalinclude:: start.py
