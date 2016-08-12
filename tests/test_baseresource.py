import unittest
import datetime

from betfairlightweight.resources.baseresource import BaseResource

from tests.tools import create_mock_json


class BaseResourceInit(unittest.TestCase):

    def test_init(self):
        base_resource = BaseResource()
        assert base_resource.Meta.identifier == 'id'
        assert base_resource.Meta.attributes == {'id': 'id'}
        assert base_resource.Meta.sub_resources == {}
        assert base_resource.Meta.datetime_attributes == ()
        assert base_resource.Meta.data_type == []
        assert base_resource.datetime_sent is None
        assert base_resource.datetime_created is not None
        assert base_resource.datetime_updated is not None
        assert base_resource.elapsed_time is None
        assert base_resource.id is None
        with self.assertRaises(AttributeError):
            assert base_resource.not_in

    def test_data(self):
        mock_response = create_mock_json('tests/resources/base_resource.json')
        base_resource = BaseResource(date_time_sent=datetime.datetime(2003, 8, 4, 12, 30, 45),
                                     **mock_response.json())

        assert base_resource.datetime_sent == datetime.datetime(2003, 8, 4, 12, 30, 45)
        assert base_resource.id == 12345
        assert base_resource.elapsed_time > 0

    def test_data_sub(self):
        mock_response = create_mock_json('tests/resources/base_resource_sub.json')

        class Model(BaseResource):
            class Meta(BaseResource.Meta):
                identifier = 'model'
                attributes = {'MainId': 'main_id',
                              'SubId': 'sub_id'}
                sub_resources = {'Id': BaseResource}

        model_response = Model(**mock_response.json())

        assert model_response.main_id == 12345
        assert model_response.id.id == 6789
        assert model_response.sub_id is None

        with self.assertRaises(AttributeError):
            assert model_response.not_in

    def test_data_empty_sub(self):
        mock_response = create_mock_json('tests/resources/base_resource.json')

        class Model(BaseResource):
            class Meta(BaseResource.Meta):
                identifier = 'model'
                attributes = {'id': 'main_id'}
                sub_resources = {'SubId': BaseResource}

        model_response = Model(**mock_response.json())
        assert model_response.main_id == 12345
        assert model_response.id == []

    def test_strip_datetime(self):
        base_resource = BaseResource()
        for string in ['2100-06-01T10:10:00.000Z', '2100-06-01T10:10:00.00Z', '2100-06-01T10:10:00.0Z']:
            stripped = base_resource.strip_datetime(string)
            assert type(stripped) == datetime.datetime

        stripped = base_resource.strip_datetime(None)
        assert not stripped

        stripped = base_resource.strip_datetime('45')
        assert not stripped

        integer = 1465631675000
        stripped = base_resource.strip_datetime(integer)
        assert type(stripped) == datetime.datetime

        stripped = base_resource.strip_datetime(None)
        assert not stripped

        stripped = base_resource.strip_datetime('45')
        assert not stripped

    def test_strip_datetime_resource(self):
        mock_response = create_mock_json('tests/resources/base_resource_sub.json')

        class Model(BaseResource):
            class Meta(BaseResource.Meta):
                identifier = 'model'
                attributes = {'MainId': 'main_id',
                              'Datetime': 'datetime',
                              'DatetimeInt': 'datetime_int',
                              'DatetimeWrong': 'datetime_wrong'}
                sub_resources = {'Id': BaseResource}
                datetime_attributes = ('Datetime', 'DatetimeInt', 'DatetimeWrong')

        model_response = Model(**mock_response.json())

        assert model_response.main_id == 12345
        assert model_response.id.id == 6789
        assert model_response.datetime == datetime.datetime.strptime('2100-06-01T10:10:00.0Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        assert model_response.datetime_int == datetime.datetime.fromtimestamp(1465631675000 / 1e3)
        assert model_response.datetime_wrong == 'wrong'

    def test_data_dict(self):
        mock_response = create_mock_json('tests/resources/base_resource_dict.json')

        class Runner(BaseResource):
            class Meta(BaseResource.Meta):
                identifier = 'runners'
                attributes = {'Id': 'id',
                              'name': 'name'}

        class Model(BaseResource):
            class Meta(BaseResource.Meta):
                identifier = 'model'
                attributes = {'Id': 'id'}
                sub_resources = {'Runners': Runner}
                dict_attributes = {'Runners': 'Id'}

        model_response = Model(**mock_response.json())

        assert model_response.id == 12345
        assert len(model_response.runners) == 2
        assert model_response.runners.get(1234) is not None
        assert model_response.runners[1234].name == 'second'

    def test_sub_resource_identifiers(self):
        base_resource = BaseResource()
        assert base_resource.sub_resource_mapping == {}

    def test_str(self):
        base_resource = BaseResource()
        assert str(base_resource) == 'BaseResource'
