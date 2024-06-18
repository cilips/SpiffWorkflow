介绍
============

考虑到许多工作流的长期运行特性，强健的序列化功能对于任何类型的工作流执行库。
在序列化工作流时，我们面临以下几个问题：

- 工作流可能包含任意数据，这些数据的序列化机制无法构建到库本身中
- 工作流可能包含自定义任务，而且这些任务也不能内置到库中
- 工作流可能包含数百个任务，生成非常大的序列化
- 工作流数据中包含的对象也可能非常大
- 序列化的数据需要存储在某个地方，并且没有一种一刀切的方法

在本文档的第一部分中，我们将展示如何处理第一个问题。

:doc:`custom_task_spec` 包含处理第二个问题的示例。

在本文档的第二部分中，我们将讨论通过创造性地使用序列化程序的功能来缓解剩余问题的一些方法。

.. _serializing_custom_objects:

序列化自定义对象
==========================

在 :doc:`script_engine`, 我们将一些自定义方法和对象添加到脚本环境中。
我们创建一个简单的类 (:code:`namedtuple`) 其保存每个产品的产品信息。

我们希望能够保存和恢复我们的自定义对象。 此代码位于 :app:`spiff/product_info.py` 。

.. code:: python

    ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])

    def product_info_to_dict(obj):
        return {
            'color': obj.color,
            'size': obj.size,
            'style': obj.style,
            'price': obj.price,
        }

    def product_info_from_dict(dct):
        return ProductInfo(**dct)

同时在 :app:`spiff/custom_object.py`:

.. code-block:: python

    from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
    from ..serializer.file import FileSerializer

    registry = FileSerializer.configure(SPIFF_CONFIG)
    registry.register(ProductInfo, product_info_to_dict, product_info_from_dict)
    serializer = FileSerializer(dirname, registry=registry)

在这个例子中，我们没有任何自定义任务规范，所以我们可以使用我们正在使用的模块的默认序列化程序配置。
我们将使用 :app:`spiff/serializer/file/serializer.py` 序列化器。
这是一个非常简单的序列化程序——它将整个工作流转换为默认的JSON格式，并以可读的方式将其写入磁盘。

.. note::

     :code:`BpmnWorkflowSerializer` 默认有一个 `serialize_json` 方法, 本质上做同样的事情，
    除非不格式化JSON。我们绕过这一点，这样我们就可以截取JSON可序列化表示，并将其自己写入我们选择的位置。

我们初始化 :code:`registry` 使用所述序列化程序；此注册表包含工作流内部使用的对象的转换。

现在，我们可以使用 :code:`registry.register` 方法。这里的论点是：

- 需要序列化的类
- 创建对象的字典表示的方法
- 从该表示重新创建对象的方法

注册对象将建立类与序列化和反序列化方法之间的关系。

这个 :code:`register` 方法分配了一个 :code:`typename` 对于该类，
并生成部分函数，这些函数基于 :code:`typename`, 并存储*这些*转换机制。

.. note::

    提供的 :code:`to_dict` 和 :code:`from_dict` 方法必须始终返回和接受字典，即使它们可能已经以其他方式序列化。

    如果您对它的工作方式感兴趣，注册表的核心是
    `DictionaryConverter <https://github.com/sartography/SpiffWorkflow/blob/main/SpiffWorkflow/bpmn/serializer/helpers/dictionary.py>`_.

    代价是一种稍微不那么可定制的序列化格式；
好处是这些部分函数可以取代巨大的 :code:`if/else` 测试特定类和属性的块。

优化序列化
=========================

文件序列化程序
---------------

现在我们将转到我们在 :app:`serializer/file/serializer.py`.

我们已经扩展了 :code:`BpmnWorkflowSerializer` 获取一个目录，我们将在其中编写文件，此外，我们将在此字典中强加一些结构。
我们将从实例数据中分离序列化的工作流规范，并设置我们可以实际读取的输出格式。

我们的引擎需要来自我们的序列化程序的特定API，这就是其余方法。
我们不会在这里讨论这些方法，因为它们实际上与库没有太大关系。我们用很少 (the
:app:`spiff/custom_object.py`) 或者没有修改 (the :app:`spiff/file.py`) 所以没什么可讨论的。

We call `self.to_dict` 和 `self.from_dict`, 根据我们设置的方式处理所有转换
:code:`registry`.

.. note::

    我们没有引用任何特定的代码，因为这里几乎所有的代码都是关于管理目录结构和适当格式化JSON输出的。

文件序列化程序实际上并没有经过特别优化，但它很容易理解，同时还提供你可能想做得更多的证据。
这里的输出基本上就是默认情况下得到的结果。
这很有用，可以很容易地看到内部和内部，如果你检查它，你会发现有很多机会将输出拆分为其组件并单独处理它们。

SQLite序列化程序
-----------------

我们有第二个示例序列化程序，它将序列化存储在中的SQLite数据库中 :app:`serializer/sqlite/serializer.py`.
这可能是您想要做的事情的一个稍微更现实的用例，
因此，我们将对此进行更详细的讨论（但这也是一个相当复杂的示例）。

我们的数据库模式实际上承担了大部分工作，但由于这不是SQL教程，我只向您介绍包含它的文件：:app:`serializer/sqlite/schema.sql`.
当然，您不必直接与数据库交互（甚至根本不必使用数据库），所有触发器和视图等中的一些都可以用Python代码替换（如果使用更健壮的数据库，则可以简化很多）。

这是一个有点极端的例子，目的是表明你真的不必检索和存储一个巨大的blob，处理它的逻辑也不必与代码的其余部分穿插在一起。

除了触发器之外，我们还非常依赖SQLite适配器。在这两件事之间，我们几乎不必担心我们得到的物体的类型！

来自我们的 :code:`execute` 方法:

.. code-block:: python

    conn = sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.execute("pragma foreign_keys=on")
    sqlite3.register_adapter(UUID, lambda v: str(v))
    sqlite3.register_converter("uuid", lambda s: UUID(s.decode('utf-8')))
    sqlite3.register_adapter(dict, lambda v: json.dumps(v))
    sqlite3.register_converter("json", lambda s: json.loads(s))

我们使用 :code:`UUID` 用于规范和实例ID，并将我们所有的工作流数据存储为JSON。
我们的序列化程序保证它的输出将是JSON可序列化的，所以当我们存储它时，我们可以将它的输出直接放入DB，并将DB输出反馈到序列化程序中。

为了帮助这个过程，我们为我们的规格定制了一些默认转换。

.. code-block:: python

    class WorkflowConverter(BpmnWorkflowConverter):

        def to_dict(self, workflow):
            dct = super(BpmnWorkflowConverter, self).to_dict(workflow)
            dct['bpmn_events'] = self.registry.convert(workflow.bpmn_events)
            dct['subprocesses'] = {}
            dct['tasks'] = list(dct['tasks'].values())
            return dct

    class SubworkflowConverter(BpmnSubWorkflowConverter):

        def to_dict(self, workflow):
            dct = super().to_dict(workflow)
            dct['tasks'] = list(dct['tasks'].values())
            return dct

    class WorkflowSpecConverter(BpmnProcessSpecConverter):

        def to_dict(self, spec):
            dct = super().to_dict(spec)
            dct['task_specs'] = list(dct['task_specs'].values())
            return dct

我们在这里没有进行广泛的自定义，主要是将一些词典切换为列表；这是因为我们将这些项存储在单独的表中，
因此可以方便地获得可以直接传递给的输出 :code:`insert` statement.

当我们配置引擎时，我们会更新序列化程序配置以使用这些类, 此代码来自 :app:`spiff/sqlite.py`:

.. code-block:: python

    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
    from ..serializer.sqlite import (
        SqliteSerializer,
        WorkflowConverter,
        SubworkflowConverter,
        WorkflowSpecConverter
    )

    DEFAULT_CONFIG[BpmnWorkflow] = WorkflowConverter
    DEFAULT_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
    DEFAULT_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

    dbname = 'spiff.db'

    with sqlite3.connect(dbname) as db:
        SqliteSerializer.initialize(db)

    registry = SqliteSerializer.configure(DEFAULT_CONFIG)
    serializer = SqliteSerializer(dbname, registry=registry)

最后，让我们看看我们为引擎所需的API实现的两种方法：

.. code-block:: python

    def _create_workflow(self, cursor, workflow, spec_id):
        dct = super().to_dict(workflow)
        wf_id = uuid4()
        stmt = "insert into workflow (id, workflow_spec_id, serialization) values (?, ?, ?)"
        cursor.execute(stmt, (wf_id, spec_id, dct))
        if len(workflow.subprocesses) > 0:
            cursor.execute("select serialization->>'name', descendant from spec_dependency where root=?", (spec_id, ))
            dependencies = dict((name, id) for name, id in cursor)
            for sp_id, sp in workflow.subprocesses.items():
                cursor.execute(stmt, (sp_id, dependencies[sp.spec.name], self.to_dict(sp)))
        return wf_id

    def _get_workflow(self, cursor, wf_id, include_dependencies):
        cursor.execute("select workflow_spec_id, serialization as 'serialization [json]' from workflow where id=?", (wf_id, ))
        row = cursor.fetchone()
        spec_id, workflow = row[0], self.from_dict(row[1])
        if include_dependencies:
            workflow.subprocess_specs = self._get_subprocess_specs(cursor, spec_id)
            cursor.execute(
                "select descendant as 'id [uuid]', serialization as 'serialization [json]' from workflow_dependency where root=? order by depth",
                (wf_id, )
            )
            for sp_id, sp in cursor:
                task = workflow.get_task_from_id(sp_id)
                workflow.subprocesses[sp_id] = self.from_dict(sp, task=task, top_workflow=workflow)
        return workflow

我们将子流程存储在与顶级流程相同的表中，因为它们本质上是相同的。
我们维护一个表，该表将父/子关系存储在一个单独的规范依赖关系表中。虽然我们目前没有这样做，
但我们可以修改查询以忽略检索工作流时已完成的子流程：它们可能包含许多永远不会被重新访问的任务。
或者，相反地，我们可以将恢复的内容限制在具有 :code:`READY` 任务，以避免加载正在等待两周后启动的计时器的内容。

我们没有显示用于序列化工作流规范的代码，但它是相似的——所有规范，无论是顶级规范还是子流程和调用活动的规范，
都位于一个表中，第二个表跟踪它们之间的依赖关系。这将使您可以等待加载规范，直到需要执行与其相关联的任务。

我们还将任务数据与工作流状态信息分开维护；
因此，虽然我们现在不这么做，但它提供了选择性地检索它的可能性——例如，它可以从中省略 :code:`COMPLETED` 任务.

我在这里要传达的是，有很多可能性可以自定义应用程序如何序列化其工作流——您不局限于默认情况下获得的巨大JSON blob。


序列化版本
======================

当我们对Spiff进行更改时，我们可能会更改序列化格式。例如，在1.2.1中，我们更改了
如何在BPMN工作流中相互处理子流程，并更新了它们的序列化方式，我们将序列化程序版本升级到1.1。

由于工作流可以包含任意数据，甚至SpiffWorkflow的内部类也被设计为以可能需要特殊序列化和反序列化的方式进行自定义，
因此可以覆盖默认版本号，为用户提供跟踪自己更改的方法。

如果您没有提供自定义版本号，SpiffWorkflow将尝试将工作流从一个版本迁移到下一个版本（如果它们是以早期格式序列化的）。

如果您已经重写了序列化程序版本，您可能需要将我们的序列化更改为你自己的。您可以在
`SpiffWorkflow/bpmn/serilaizer/migrations <https://github.com/sartography/SpiffWorkflow/tree/main/SpiffWorkflow/bpmn/serializer/migration>`_
中找到我们的迁移, 这些功能被分解为处理每个单独更改的功能，这有望使它们更容易融入升级过程，并提供一些关于更改内容的文档。
