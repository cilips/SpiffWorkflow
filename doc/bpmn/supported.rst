支持的元素列表
==========================

任务
-----

* User Task
* Manual Task
* Business Rule Task
* Script Task
* Service Task

.. note::

    Spiff对服务任务的实现是抽象的，因此在解析它们时，库没有提供用于执行它们的内置机制。

网关
--------

* Parallel Gateway
* Exclusive Gateway
* Inclusive Gateway
* Event-Based Gateway

子进程和调用活动
-------------------------------

* Subprocess
* Call Activity
* Transaction Subprocess

事件
------

* Cancel Event
* Escalation Event
* Error Event
* Message Event
* Signal Event
* Terminate Event
* Timer Event

数据
----

* Data Object
* Data Store

.. note::

    Spiff的数据存储实现是抽象的；Spiff可以解析数据存储，但不提供任何内置的读写机制。

循环
-----

* Loop Task
* Parallel MultiInstance Task
* Sequential MultiInstance Task


.. note::

    并行多实例任务不是由SpiffWorkflow并行执行的。SpiffWorkflow仅指示并行任务同时准备就绪，并且工作流引擎可以并行执行这些任务。
