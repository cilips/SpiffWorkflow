日志
=======

Spiff提供了几个记录器：
 -  :code:`spiff` 记录器, 它在初始化工作流和任务更改状态时发出消息
 -  :code:`spiff.metrics` 记录器, 它发出包含任务经过的持续时间的消息

在运行工作流过程中创建的所有日志条目都包含以下额外属性：

- :code:`workflow_spec`: 当前工作流规范的名称
- :code:`task_spec`: 任务规范的名称
- :code:`task_id`: 任务的ID
- :code:`task_type`: 任务的规范类的名称

如果日志级别小于20:

- :code:`data` 任务数据（可能很大，仅用于调试目的）

如果日志级别小于或等于10：

- :code:`internal_data`: 任务内部数据（仅在DEBUG或更低版本中可用，因为它通常不有用）

metrics logger 还提供并仅在DEBUG级别发出消息：

- :code:`elapsed`: 任务运行所花费的时间（例如, :code:`task.run` 方法的持续时间)

在我们的命令行UI中 (:app:`cli/subcommands.py`), 我们在日志记录中添加了一些额外的属性：

.. code-block:: python

    spiff_logger = logging.getLogger('spiff')
    spiff_handler = logging.StreamHandler()
    spiff_handler.setFormatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(message)s')
    spiff_logger.addHandler(spiff_handler)

    metrics_logger = logging.getLogger('spiff.metrics')
    metrics_handler = logging.StreamHandler()
    metrics_handler.setFormatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(elasped)s')
    metrics_logger.addHandler(metrics_handler)

在配置模块中 :app:`spiff/file.py` 出现在许多示例中，我们设置 :code:`spiff`
logger 到 :code:`INFO`, 因此，我们将看到有关任务状态更改的消息，但忽略度量日志；
然而，配置可以很容易地更改为包含它（但是，它可能会生成大量非常大的记录，所以请注意警告！）。

