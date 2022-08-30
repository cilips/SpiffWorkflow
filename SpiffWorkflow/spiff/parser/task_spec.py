from lxml import etree

from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import SubprocessParser
from SpiffWorkflow.bpmn.parser.util import xpath_eval

SPIFFWORKFLOW_MODEL_NS = 'http://spiffworkflow.org/bpmn/schema/1.0/core'


class SpiffTaskParser(TaskParser):

    def parse_extensions(self, node=None):
        # Too bad doing this works in such a stupid way.
        # We should set a namespace and automatically do this.
        extensions = {}
        extra_ns = {'spiffworkflow': SPIFFWORKFLOW_MODEL_NS}
        xpath = xpath_eval(self.node, extra_ns) if node is None else xpath_eval(node, extra_ns)
        extension_nodes = xpath('.//bpmn:extensionElements/spiffworkflow:*')
        for node in extension_nodes:
            name = etree.QName(node).localname
            if name == 'properties':
                extensions['properties'] = self._parse_properties(node)
            else:
                extensions[name] = node.text
        return extensions

    def _parse_properties(self, node):
        extra_ns = {'spiffworkflow': SPIFFWORKFLOW_MODEL_NS}
        xpath = xpath_eval(node, extra_ns)
        property_nodes = xpath('.//spiffworkflow:property')
        properties = {}
        for prop_node in property_nodes:
            properties[prop_node.attrib['name']] = prop_node.attrib['value']
        return properties

    def create_task(self):
        # The main task parser already calls this, and even sets an attribute, but
        # 1. It calls it after creating the task so I don't have access to it here yet and
        # 2. I want defined attributes, not a dict of random crap
        # (though the dict of random crap will still be there since the base parser adds it).
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return self.spec_class(self.spec, self.get_task_spec_name(),
                               lane=self.lane,
                               description=self.node.get('name', None),
                               position=self.position,
                               prescript=prescript,
                               postscript=postscript)


class SubWorkflowParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            prescript=prescript,
            postscript=postscript)


class CallActivityParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            prescript=prescript,
            postscript=postscript)


class BusinessRuleTaskParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        decision_ref = extensions.get('calledDecisionId')
        return BusinessRuleTask(self.spec,
            self.get_task_spec_name(),
            dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
            lane=self.lane,
            position=self.position,
            description=self.node.get('name', None)
        )