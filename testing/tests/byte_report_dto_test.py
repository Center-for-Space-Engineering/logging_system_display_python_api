import pytest

from logging_system_display_python_api.DTOs.byte_report import byte_report_dto

byte_report = byte_report_dto("test thread", '08-06-1945_08:15', 8128)

@pytest.mark.byte_report_dto_tests
def test__init__():
    assert byte_report._byte_report_dto__thread_name == "test thread"
    assert byte_report._byte_report_dto__time == "08-06-1945_08:15"
    assert byte_report._byte_report_dto__byte_count == 8128

def test_get_time():
    assert byte_report.get_time() == "08-06-1945_08:15"

def test_get_thread_name():
    assert byte_report.get_thread_name() == "test thread"

def test_get_byte_count():
    assert byte_report.get_byte_count() == 8128

def test__str__():
    time = byte_report.get_time()
    byte_count = byte_report.get_byte_count()
    assert str(byte_report) == f"Bytes received at: [{time}]" + " |" + str(byte_count)