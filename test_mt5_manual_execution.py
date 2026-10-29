import unittest
from types import SimpleNamespace as NS
from mt5_manual_execution import ManualOrder, ExecutionBlocked, send_manual_order, required_confirmation

class FakeMT5:
    ACCOUNT_TRADE_MODE_DEMO = 0; ACCOUNT_TRADE_MODE_REAL = 2
    ORDER_TYPE_BUY = 0; ORDER_TYPE_SELL = 1; TRADE_ACTION_DEAL = 1; ORDER_TIME_GTC = 0
    TRADE_RETCODE_DONE = 10009; TRADE_RETCODE_PLACED = 10008
    def __init__(self, mode=0, pnl=-10):
        self.account = NS(trade_mode=mode, equity=10000, trade_allowed=True)
        self.terminal = NS(connected=True, trade_allowed=True)
        self.info = NS(visible=True, trade_allowed=True, point=.00001, volume_min=.01,
                       volume_max=10, volume_step=.01, trade_stops_level=0, filling_mode=1)
        self.tick = NS(bid=1.10000, ask=1.10010)
        self.pnl = pnl; self.sent=[]
    def terminal_info(self): return self.terminal
    def account_info(self): return self.account
    def symbol_info(self, _): return self.info
    def symbol_info_tick(self, _): return self.tick
    def symbol_select(self, *_): return True
    def positions_get(self, **_): return []
    def order_calc_profit(self, *_): return self.pnl
    def order_check(self, _): return NS(retcode=self.TRADE_RETCODE_DONE, comment="ok")
    def order_send(self, req): self.sent.append(req); return NS(retcode=self.TRADE_RETCODE_DONE, order=123)
    def last_error(self): return "fake"

class ExecutionTests(unittest.TestCase):
    def setUp(self): self.order=ManualOrder("EURUSD", "BUY", .01, 1.09, 1.12, 30, .25)
    def test_demo_order_requires_exact_confirmation_and_submits_once(self):
        mt=FakeMT5(); ack=required_confirmation(self.order,False)
        result=send_manual_order(mt,self.order,ack)
        self.assertEqual(result.status,"SUBMITTED"); self.assertEqual(len(mt.sent),1)
    def test_bad_confirmation_never_sends(self):
        mt=FakeMT5()
        with self.assertRaises(ExecutionBlocked): send_manual_order(mt,self.order,"yes")
        self.assertEqual(mt.sent,[])
    def test_real_requires_opt_in(self):
        mt=FakeMT5(FakeMT5.ACCOUNT_TRADE_MODE_REAL)
        with self.assertRaises(ExecutionBlocked): send_manual_order(mt,self.order,required_confirmation(self.order,True))
        self.assertEqual(mt.sent,[])
    def test_risk_cap_blocks(self):
        mt=FakeMT5(pnl=-100)
        with self.assertRaises(ExecutionBlocked): send_manual_order(mt,self.order,required_confirmation(self.order,False))
        self.assertEqual(mt.sent,[])
    def test_open_position_blocks_duplicate(self):
        mt=FakeMT5(); mt.positions_get=lambda **_: [object()]
        with self.assertRaises(ExecutionBlocked): send_manual_order(mt,self.order,required_confirmation(self.order,False))
        self.assertEqual(mt.sent,[])
    def test_terminal_algo_trading_disabled_blocks(self):
        mt=FakeMT5(); mt.terminal.trade_allowed=False
        with self.assertRaises(ExecutionBlocked): send_manual_order(mt,self.order,required_confirmation(self.order,False))
        self.assertEqual(mt.sent,[])

if __name__ == "__main__": unittest.main()
