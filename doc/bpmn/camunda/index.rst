使用Camunda配置模块
======================================

.. warning:: 有更好的方法 ...
  SpiffWorkflow并不旨在支持Camunda的所有专有扩展。
  Camunda Properties Panel中的许多项目都不起作用, SpiffWorkflow的主要功能（消息、数据对象、服务任务、预脚本等）
  无法在Camunda编辑器中进行配置。
  使用 `SpiffArena <https://www.spiffworkflow.org/posts/articles/get_started/>`_
  转而构建和测试BPMN模型！

SpiffWorkflow的早期用户严重依赖Camunda的建模器，我们的几个任务规范实现都是基于Camunda扩展的。
对这些扩展的支持已转移到:code:`camunda`包中。
我们不会积极维护此软件包（尽管我们将接受Camunda用户的贡献！）。
请注意，将出现在Camunda编辑器中的许多Camunda扩展不适用于SpiffWorkflow。


在本回购中，我们提供以下配置：

.. code-block:: console

   ./runner.py -e spiff_example.camunda.sqlite

任务
=====

用户任务
----------

创建用户任务
^^^^^^^^^^^^^^^^^^^^

当您在BPMN建模器中单击用户任务时，属性面板会包含一个表单选项卡。使用此选项卡可以构建问题。

以下示例显示如何在Camumda中设置表单。

.. figure:: figures/user_task.png
   :scale: 30%
   :align: center

   User Task configuration


手动任务
------------

创建手动任务
^^^^^^^^^^^^^^^^^^^^^^

我们可以使用BPMN元素Documentation字段来显示有关项目上下文的更多信息。

Spiff的设置方式可以使用任何您想要的模板库，但我们使用了
`Jinja <https://jinja.palletsprojects.com/en/3.0.x/>`_.

在本例中，我们将向客户提供订单摘要。

.. figure:: figures/documentation.png
   :scale: 30%
   :align: center

   元素文档

示例代码
------------

示例人工任务处理程序可以在:app:`camunda/curses_handlers.py`中找到。

事件
======

消息事件
--------------

配置消息事件
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: figures/throw_message_event.png
   :scale: 60%
   :align: center

   抛出消息事件配置


.. figure:: figures/message_start_event.png
   :scale: 60%
   :align: center

   消息捕获事件配置

Throw Message Event Implementation 应为 'Expression' ，Expression应为可求值的Python语句。
在本例中，我们只发送 :code:`reason_delayed` 变量的内容，该变量包含“调查延迟”的响应任务


我们可以为结果变量提供一个名称，但我在这里没有这样做，因为事件的生成器告诉处理程序调用什么值对我来说没有意义。
如果您 *do* 指定了一个结果变量，那么消息负载（在抛出任务的上下文中计算的表达式）将被添加到该名称的变量中的处理任务的数据中；
如果保留为空，SpiffWorkflow将创建一个形式为<Handling Task Name>_Response的变量。

多实例任务
===================

早期版本的SpiffWorkflow依赖于Camunda多实例面板中的可用属性。

.. figure:: figures/multiinstance_task_configuration.png
   :scale: 60%
   :align: center

   多实例任务配置

SpiffWorkflow在 :code:`camunda` 包中有一个多实例任务规范，该规范以以下方式解释这些字段：


* Loop Cardinality:

   - 如果这是一个整数，或者是一个计算结果为整数的变量，则该数字将用于确定实例的数量
   - 如果这是一个集合，则集合的大小将用于确定实例的数量

* Collection: 输出集合（输入集合必须在 "Cardinality" 字段中指定）。

* Element variable: 要为每个实例将项复制到的变量的名称。

.. warning::

   此包中的规格基于旧版本的Camunda，因此面板可能已更改。
   这些属性可能是Camunda使用这些字段的方式，也可能不是，也可能与更新或当前版本相似*使用风险自负*
