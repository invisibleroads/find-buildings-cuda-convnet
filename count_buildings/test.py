import geometryIO
from mock import patch
from pyramid.testing import DummyRequest
from unittest import TestCase

from . import view
from crosscompute import models as m
from crosscompute.libraries import validation as v


process = view.count_buildings_
result = m.Result(
    id=1,
    name=u'whee',
    summary={'columns': ['a', 'b']})


class ViewTest(TestCase):

    def test_no_parameters_given(self):
        request = DummyRequest()
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.REQUIRED in errors['source_table'])
        self.assert_(v.REQUIRED in errors['column_x_index'])
        self.assert_(v.REQUIRED in errors['column_y_index'])
        self.assert_(v.REQUIRED in errors['source_proj4'])
        self.assert_(v.REQUIRED in errors['target_proj4'])

    @patch('crosscompute.models.Result.get')
    def test_source_table_not_found(self, get):
        get.side_effect = v.ResultIndexError
        request = DummyRequest({'source_table': 'xxx'})
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.INVALID in errors['source_table'])

    @patch('crosscompute.models.Result.get')
    def test_source_table_denied(self, get):
        get.side_effect = v.ResultAccessError
        request = DummyRequest({'source_table': '10'})
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.DENIED in errors['source_table'])

    @patch('crosscompute.models.Result.get')
    def test_column_index_invalid_number(self, get):
        get.return_value = result
        request = DummyRequest({
            'source_table': '1',
            'column_x_index': 'xxx',
            'column_y_index': 'yyy',
            'source_proj4': geometryIO.proj4LL,
            'target_proj4': geometryIO.proj4SM,
        })
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.INVALID in errors['column_x_index'])
        self.assert_(v.INVALID in errors['column_y_index'])

    @patch('crosscompute.models.Result.get')
    def test_column_index_invalid_index(self, get):
        get.return_value = result
        request = DummyRequest({
            'source_table': '1',
            'column_x_index': '100',
            'column_y_index': '101',
            'source_proj4': geometryIO.proj4LL,
            'target_proj4': geometryIO.proj4SM,
        })
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.INVALID in errors['column_x_index'])
        self.assert_(v.INVALID in errors['column_y_index'])

    @patch('crosscompute.models.Result.get')
    def test_proj4_invalid(self, get):
        get.return_value = result
        request = DummyRequest({
            'source_table': '1',
            'column_x_index': '1',
            'column_y_index': '2',
            'source_proj4': 'xxx',
            'target_proj4': 'yyy',
        })
        data = process(request)
        errors = data['errors']
        self.assertEqual(400, request.response.status_code)
        self.assert_(v.INVALID in errors['source_proj4'])
        self.assert_(v.INVALID in errors['target_proj4'])

    @patch('crosscompute.libraries.queue.schedule')
    @patch('crosscompute.models.Result.get')
    def test_success(self, get, schedule):
        get.return_value = result
        request = DummyRequest({
            'source_table': '1',
            'column_x_index': '0',
            'column_y_index': '1',
            'source_proj4': unicode(geometryIO.proj4LL),
            'target_proj4': unicode(geometryIO.proj4SM),
        })
        process(request)
        self.assertEqual(200, request.response.status_code)
        columns = result.summary['columns']
        params = request.params
        schedule.assert_called_once_with(
            request, view.schedule.start, result.name, result.id,
            columns[int(params['column_x_index'])],
            columns[int(params['column_y_index'])],
            params['source_proj4'],
            params['target_proj4'])
