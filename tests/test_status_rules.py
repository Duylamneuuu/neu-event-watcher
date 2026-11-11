import unittest
from neu_event_watcher.status_rules import classify_status, fingerprint


class TestStatus(unittest.TestCase):
    def test_sold_out(self):
        self.assertEqual(classify_status('Sea-Novation | Hết vé')[0], 'SOLD_OUT')

    def test_early_close(self):
        self.assertEqual(classify_status('BTC THÔNG BÁO ĐÓNG ĐƠN TRƯỚC THỜI HẠN')[0], 'CLOSED')

    def test_no_false_open(self):
        self.assertEqual(classify_status('Đăng ký đến 13/11, sự kiện 16/11')[0], 'UNCERTAIN')

    def test_no_false_sold_out_when_negated(self):
        self.assertEqual(classify_status('Hiện tại chưa hết vé, mời đăng ký')[0], 'UNCERTAIN')

    def test_no_false_closed_when_negated(self):
        self.assertEqual(classify_status('BTC chưa đóng đơn, các bạn đăng ký tiếp')[0], 'UNCERTAIN')

    def test_has_stable_hash(self):
        self.assertEqual(fingerprint('  Xin  Chào\n'), fingerprint('xin chào'))


if __name__ == '__main__':
    unittest.main()
