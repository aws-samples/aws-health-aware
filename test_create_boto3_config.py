import handler
import pytest


@pytest.mark.parametrize('region', ['us-east-1', 'us-east-2'])
def test_boto3_config_object(region, mocker):
    """When the DNS record changes for the health API the config should be updated correctly"""
    mock_gethostname = mocker.patch('handler.socket.gethostbyname_ex')
    mock_gethostname.return_value = (f'health.{region}.amazonaws.com', ['global.health.amazonaws.com'], ['52.94.233.29'])
    assert handler.create_boto3_config().region_name == region
