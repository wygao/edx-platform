import logging
import random

from xmodule.x_module import XModule
from xmodule.seq_module import SequenceDescriptor

from lxml import etree

from xblock.fields import Scope, Integer, Dict
from xblock.fragment import Fragment

log = logging.getLogger('edx.' + __name__)


class SplitTestFields(object):
    experiment_id = Integer(help="Which experiment is used",
                            scope=Scope.content)

    # condition_id is an int
    # child is a serialized UsageId (aka Location).  This child
    # location needs to actually match one of the children of this
    # Block.  (expected invariant that we'll need to test, and handle
    # authoring tools that mess this up)

    # TODO: is there a way to add some validation around this, to
    # be run on course load or in studio or ....

    condition_id_to_child = Dict(help="Which child module students in a particular condition_id should see",
                                 scope=Scope.content)


class SplitTestModule(SplitTestFields, XModule):
    """
    Show the user the appropriate child.  Uses the ExperimentState
    API to figure out which child to show.

    Technical notes:
      - There is more dark magic in this code than I'd like.  The whole varying-children +
        grading interaction is a tangle between super and subclasses of descriptors and
        modules.
"""
    def __init__(self, *args, **kwargs):
        super(SplitTestFields, self).__init__(*args, **kwargs)

        # TODO: add code to runtime to call Experiments API with
        # the current user_id
        #import pudb; pudb.set_trace()
        condition_id = self.runtime.get_condition_for_user(self.experiment_id)

        # condition_id_to_child comes from json, so it has to have string keys
        str_condition_id = str(condition_id)
        if str_condition_id in self.condition_id_to_child:
            child_location = self.condition_id_to_child[str_condition_id]
            self.child_descriptor = self.get_child_descriptor_by_location(child_location)
        else:
            # Oops.  Config error.
            # TODO: better error message
            log.debug("split test config error: invalid condition_id.  Showing error")
            self.child_descriptor = None

        if self.child_descriptor is not None:
            # Peak confusion is great.  Now that we set child_descriptor,
            # get_children() should return a list with one element--the
            # xmodule for the child
            self.child = self.get_children()[0]
        else:
            # TODO: better error message
            log.debug("split test config error: no such child")
            self.child = None


    def get_child_descriptor_by_location(self, location):
        """
        Look through the children and look for one with the given location.
        Returns the descriptor.
        If none match, return None
        """
        # NOTE: calling self.get_children() creates a circular reference--
        # it calls get_child_descriptors() internally, but that doesn't work until
        # we've picked a choice.  Use self.descriptor.get_children() instead.

        for child in self.descriptor.get_children():
            if child.location.url() == location:
                return child

        return None


    def get_child_descriptors(self):
        """
        For grading--return just the chosen child.
        """
        if self.child_descriptor is None:
            return []

        return [self.child_descriptor]


    def student_view(self, context):
        if self.child is None:
            # raise error instead?  In fact, could complain on descriptor load...
            return Fragment(content=u"<div>Nothing here.  Move along.</div>")

        return self.child.render('student_view', context)

    def get_icon_class(self):
        return self.child.get_icon_class() if self.child else 'other'


class SplitTestDescriptor(SplitTestFields, SequenceDescriptor):
    # the editing interface can be the same as for sequences -- just a container
    module_class = SplitTestModule

    filename_extension = "xml"

    def definition_to_xml(self, resource_fs):

        xml_object = etree.Element('split_test')
        # TODO: also save the experiment id and the condition map
        for child in self.get_children():
            xml_object.append(
                etree.fromstring(child.export_to_xml(resource_fs)))
        return xml_object

    def has_dynamic_children(self):
        """
        Grading needs to know that only one of the children is actually "real".  This
        makes it use module.get_child_descriptors().
        """
        return True
