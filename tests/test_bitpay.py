"""
BitPay Unit Tests
"""
import os
import unittest
from datetime import date, timedelta
from src.bitpay_sdk.client import Client
from src.bitpay_sdk.models.bill.bill import Bill
from src.bitpay_sdk.models.bill.item import Item
from src.bitpay_sdk.models.currency import Currency
from src.bitpay_sdk.models.invoice.buyer import Buyer
from src.bitpay_sdk.models.payout.payout import Payout
from src.bitpay_sdk.models.invoice.invoice import Invoice
from src.bitpay_sdk.models.bill.bill_status import BillStatus
from src.bitpay_sdk.models.subscription.bill_data import BillData
from src.bitpay_sdk.models.payout.payout_batch import PayoutBatch
from src.bitpay_sdk.models.payout.payout_status import PayoutStatus
from src.bitpay_sdk.models.subscription.subscription import Subscription
from src.bitpay_sdk.models.payout.payout_recipient import PayoutRecipient
from src.bitpay_sdk.models.payout.recipient_status import RecipientStatus
from src.bitpay_sdk.models.payout.payout_recipients import PayoutRecipients
from src.bitpay_sdk.models.subscription.item import Item as SubscriptionItem
from src.bitpay_sdk.models.payout.payout_instruction import PayoutInstruction
from src.bitpay_sdk.models.subscription.subscription_status import SubscriptionStatus
from src.bitpay_sdk.models.payout.recipient_reference_method import RecipientReferenceMethod


class BitPayTest(unittest.TestCase):
    """
    Unit Test functions
    """

    def setUp(self):
        self.bitpay = Client(os.path.abspath("bitpay.config.json").encode())

    def test_should_get_invoice_id(self):
        invoice = Invoice(2.16, "eur")
        invoice.set_order_id("98e572ea-910e-415d-b6de-65f5090680f6")
        invoice.set_full_notifications(True)
        invoice.set_extended_notifications(True)
        invoice.set_transaction_speed("medium")
        invoice.set_notification_url("https://hookbin.com/lJnJg9WW7MtG9GZlPVdj")
        invoice.set_redirect_url("https://hookbin.com/lJnJg9WW7MtG9GZlPVdj")
        invoice.set_pos_data("98e572ea35hj356xft8y8cgh56h5090680f6")
        invoice.set_item_desc("Ab tempora sed ut.")

        buyer = Buyer()
        buyer.set_name("Bily Matthews")
        buyer.set_email("sandbox@bitpay.com")
        buyer.set_address1("168 General Grove")
        buyer.set_address2("sandbox@bitpay.com")
        buyer.set_country("AD")
        buyer.set_locality("Port Horizon")
        buyer.set_notify(True)
        buyer.set_phone("+99477512690")
        buyer.set_postal_code("KY7 1TH")
        buyer.set_region("New Port")

        invoice.set_buyer(buyer)

        basic_invoice = self.bitpay.create_invoice(invoice)
        retrieve_invoice = self.bitpay.get_invoice(basic_invoice.get_id())

        self.assertIsNotNone(basic_invoice.get_id())
        self.assertIsNotNone(retrieve_invoice.get_id())

    def test_should_create_invoice_btc(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(2.16, "btc"))
        self.assertIsNotNone(basic_invoice.get_id())

    def test_should_create_invoice_bch(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(2.16, "bch"))
        self.assertIsNotNone(basic_invoice.get_id())

    def test_should_create_invoice_eth(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(2.16, "eth"))
        self.assertIsNotNone(basic_invoice.get_id())

    def test_should_get_invoice_URL(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(5.0, "usd"))
        self.assertIsNotNone(basic_invoice.get_url())

    def test_should_get_invoice_status(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(5.0, "usd"))
        self.assertEqual("new", basic_invoice.get_status())

    def test_should_create_invoice_one_tenth_btc(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(0.1, "btc"))
        self.assertEqual(0.1, basic_invoice.get_price())

    def test_should_create_invoice_100_usd(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(100.0, "usd"))
        self.assertEqual(100.0, basic_invoice.get_price())

    def test_should_create_invoice_100_eur(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(100.0, "eur"))
        self.assertEqual(100.0, basic_invoice.get_price())

    def test_should_get_invoice(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(5.0, "eur"))
        retrieved_invoice = self.bitpay.get_invoice(basic_invoice.get_id())

        self.assertEqual(basic_invoice.get_id(), retrieved_invoice.get_id())

    def test_should_get_invoices(self):
        today = date.today().strftime("%Y%m%d")
        date_start = (date.today() - timedelta(days=30)).strftime("%Y%m%d")
        invoices = self.bitpay.get_invoices(date_start, today, None, None, None, None)

        self.assertIsNotNone(invoices)
        self.assertGreater(len(invoices), 0)

    def test_should_create_update_and_delete_invoice(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(2, "btc"))
        retrieved_invoice = self.bitpay.get_invoice(basic_invoice.get_id())
        updated_invoice = self.bitpay.update_invoice(retrieved_invoice.get_id(),
                                                     "sandbox@bitpay.com")
        cancelled_invoice = self.bitpay.cancel_invoice(updated_invoice.get_id())
        retrieved_cancelled_invoice = self.bitpay.get_invoice(cancelled_invoice.get_id())

        self.assertIsNotNone(basic_invoice)
        self.assertIsNotNone(retrieved_invoice)
        self.assertIsNotNone(updated_invoice)
        self.assertIsNotNone(cancelled_invoice)
        self.assertIsNotNone(retrieved_cancelled_invoice)

    def test_should_request_invoice_webhook(self):
        basic_invoice = self.bitpay.create_invoice(Invoice(2, "btc"))
        result = self.bitpay.request_invoice_notifications(basic_invoice.get_id())
        self.assertTrue(result)

    def test_should_create_get_cancel_refund_request_new(self):
        today = date.today().strftime("%Y%m%d")
        date_start = (date.today() - timedelta(days=30)).strftime("%Y%m%d")
        invoices = self.bitpay.get_invoices(date_start, today, "complete", None, None, None)
        first_invoice = invoices[0]
        create_refund = self.bitpay.create_refund(first_invoice.get_id(),
                                                  1.0, "usd", True, False, False)
        retrieved_refunds = self.bitpay.get_refunds(first_invoice.get_id())
        last_refund = retrieved_refunds[-1]
        update_refund = self.bitpay.update_refund(last_refund.get_id(), "created")
        retrieved_refund = self.bitpay.get_refund(last_refund.get_id())
        notification_status = self.bitpay.request_refund_notification(last_refund.get_id())
        cancel_refund = self.bitpay.cancel_refund(last_refund.get_id())
        supported_wallets = self.bitpay.get_supported_wallets()

        self.assertIsNotNone(invoices)
        self.assertIsNotNone(create_refund.get_id())
        self.assertIsNotNone(retrieved_refunds)
        self.assertEqual("created", update_refund.get_status())
        self.assertEqual(last_refund.get_id(), retrieved_refund.get_id())
        self.assertTrue(notification_status)
        self.assertEqual("cancelled", cancel_refund.get_status())
        self.assertIsNotNone(supported_wallets)

    def test_should_create_bill_usd(self):
        items = []

        item = Item()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = Item()
        item.set_price(14.0)
        item.set_quantity(16)
        item.set_description("product-b")
        items.append(item)

        item = Item()
        item.set_price(17.0)
        item.set_quantity(24)
        item.set_description("product-c")
        items.append(item)

        item = Item()
        item.set_price(4.0)
        item.set_quantity(46)
        item.set_description("product-d")
        items.append(item)

        bill = Bill("1001", Currency.USD, "sandbox@bitpay.com", items)
        basic_bill = self.bitpay.create_bill(bill)

        self.assertIsNotNone(basic_bill.get_id())
        self.assertIsNotNone(basic_bill.get_items()[0].get_id())

    def test_should_create_bill_eur(self):
        items = []

        item = Item()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = Item()
        item.set_price(14.0)
        item.set_quantity(16)
        item.set_description("product-b")
        items.append(item)

        item = Item()
        item.set_price(17.0)
        item.set_quantity(24)
        item.set_description("product-c")
        items.append(item)

        item = Item()
        item.set_price(4.0)
        item.set_quantity(46)
        item.set_description("product-d")
        items.append(item)

        bill = Bill("1002", Currency.EUR, "sandbox@bitpay.com", items)
        basic_bill = self.bitpay.create_bill(bill)

        self.assertIsNotNone(basic_bill.get_id())
        self.assertIsNotNone(basic_bill.get_items()[0].get_id())
        self.assertEqual(BillStatus.Draft, basic_bill.get_status())
        self.assertIsNotNone(basic_bill.get_url())

    def test_should_get_bill(self):
        items = []

        item = Item()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = Item()
        item.set_price(14.0)
        item.set_quantity(16)
        item.set_description("product-b")
        items.append(item)

        item = Item()
        item.set_price(17.0)
        item.set_quantity(24)
        item.set_description("product-c")
        items.append(item)

        item = Item()
        item.set_price(4.0)
        item.set_quantity(46)
        item.set_description("product-d")
        items.append(item)

        bill = Bill("1003", Currency.USD, "sandbox@bitpay.com", items)
        basic_bill = self.bitpay.create_bill(bill)
        retrieve_bill = self.bitpay.get_bill(basic_bill.get_id())

        self.assertEqual(basic_bill.get_id(), retrieve_bill.get_id())
        self.assertEqual(basic_bill.get_items(), retrieve_bill.get_items())

    def test_should_update_bill(self):
        items = []

        item = Item()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = Item()
        item.set_price(14.0)
        item.set_quantity(16)
        item.set_description("product-b")
        items.append(item)

        item = Item()
        item.set_price(17.0)
        item.set_quantity(24)
        item.set_description("product-c")
        items.append(item)

        item = Item()
        item.set_price(4.0)
        item.set_quantity(46)
        item.set_description("product-d")
        items.append(item)

        bill = Bill("1004", Currency.EUR, "sandbox@bitpay.com", items)
        basic_bill = self.bitpay.create_bill(bill)
        retrieve_bill = self.bitpay.get_bill(basic_bill.get_id())

        self.assertEqual(basic_bill.get_id(), retrieve_bill.get_id())
        self.assertEqual(basic_bill.get_items(), retrieve_bill.get_items())
        self.assertCountEqual(4, retrieve_bill.get_items())

        items = retrieve_bill.get_items()
        item = Item()
        item.set_price(50.0)
        item.set_quantity(7)
        item.set_description("product-added")
        items.append(item)

        retrieve_bill.set_items(items)
        update_bill = self.bitpay.update_bill(retrieve_bill, retrieve_bill.get_id())
        items = update_bill.get_items()

        self.assertCountEqual(5, update_bill.get_items())
        self.assertEqual(items[-1].get_description(), "product-added")

    def test_should_get_bills(self):
        bills = self.bitpay.get_bills()

        self.assertGreater(0, len(bills))

    def test_should_get_bills_by_status(self):
        bills = self.bitpay.get_bills(BillStatus.Draft)

        self.assertGreater(0, len(bills))

    def test_should_deliver_bill(self):
        items = []

        item = Item()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = Item()
        item.set_price(14.0)
        item.set_quantity(16)
        item.set_description("product-b")
        items.append(item)

        item = Item()
        item.set_price(17.0)
        item.set_quantity(24)
        item.set_description("product-c")
        items.append(item)

        item = Item()
        item.set_price(4.0)
        item.set_quantity(46)
        item.set_description("product-d")
        items.append(item)

        bill = Bill("1005", Currency.EUR, "sandbox@bitpay.com", items)
        basic_bill = self.bitpay.create_bill(bill)
        result = self.bitpay.deliver_bill(basic_bill.get_id(),
                                          basic_bill.get_token())
        retrieve_bill = self.bitpay.get_bill(basic_bill.get_id())

        self.assertEqual(basic_bill.get_id(), retrieve_bill.get_id())
        self.assertEqual(basic_bill.get_items(), retrieve_bill.get_items())
        self.assertEqual("Success", result)
        self.assertNotEqual(basic_bill.get_status(), retrieve_bill.get_status())
        self.assertEqual(BillStatus.Sent, retrieve_bill.get_status())

    def test_should_get_ledger_usd(self):
        today = date.today().strftime("%Y%m%d")
        date_start = (date.today() - timedelta(days=7)).strftime("%Y%m%d")
        ledger = self.bitpay.get_ledger(Currency.USD, date_start, today)

        self.assertIsNotNone(ledger)
        self.assertGreater(0, len(ledger))

    def test_should_get_ledger_btc(self):
        today = date.today().strftime("%Y%m%d")
        date_start = (date.today() - timedelta(days=7)).strftime("%Y%m%d")
        ledger = self.bitpay.get_ledger(Currency.BTC, date_start, today)

        self.assertIsNotNone(ledger)
        self.assertGreater(0, len(ledger))

    def test_should_get_ledgers(self):
        ledgers = self.bitpay.get_ledgers()

        self.assertIsNotNone(ledgers)
        self.assertGreater(0, len(ledgers))

    def test_should_submit_payout_recipients(self):
        recipients_list = []

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient1")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient2")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient3")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        recipients_obj = PayoutRecipients(recipients_list)
        recipients = self.bitpay.submit_payout_recipients(recipients_obj)

        self.assertIsNotNone(recipients)
        self.assertCountEqual(3, recipients)

    def test_should_get_payout_recipient_id(self):
        recipients_list = []

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient1")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        recipients_obj = PayoutRecipients(recipients_list)
        recipients = self.bitpay.submit_payout_recipients(recipients_obj)
        first_recipient = recipients[0]
        retrieve_recipient = self.bitpay.get_payout_recipient(first_recipient.get_id())

        self.assertIsNotNone(first_recipient)
        self.assertIsNotNone(retrieve_recipient.get_id())
        self.assertEqual(first_recipient.get_id(), retrieve_recipient.get_id())

    def test_should_get_payout_recipients(self):
        recipients = self.bitpay.get_payout_recipients('active', 2)

        self.assertIsNotNone(recipients)
        self.assertCountEqual(2, recipients)

    def test_should_submit_get_and_delete_payout_recipient(self):
        recipients_list = []

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient1")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        recipients_obj = PayoutRecipients(recipients_list)
        recipients = self.bitpay.submit_payout_recipients(recipients_obj)
        first_recipient = recipients[0]
        retrieve_recipient = self.bitpay.get_payout_recipient(first_recipient.get_id())
        retrieve_recipient.set_label("updatedLabel")
        update_recipient = self.bitpay.update_payout_recipient(retrieve_recipient.get_id(),
                                                               retrieve_recipient)
        delete_recipient = self.bitpay.delete_payout_recipient(retrieve_recipient.get_id())

        self.assertIsNotNone(first_recipient)
        self.assertIsNotNone(retrieve_recipient.get_id())
        self.assertEqual(first_recipient.get_id(), retrieve_recipient.get_id())
        self.assertEqual(RecipientStatus.INVITED, retrieve_recipient.get_status())
        self.assertTrue(delete_recipient)
        self.assertEqual("updatedLabel", update_recipient.get_label())

    def test_should_request_payout_recipient_notification(self):
        recipients_list = []

        payout_recipient = PayoutRecipient()
        payout_recipient.set_email("sandbox@bitpay.com")
        payout_recipient.set_label("recipient1")
        payout_recipient.set_notification_url("https://hookb.in/QJOPBdMgRkukpp2WO60o")
        recipients_list.append(payout_recipient)

        recipients_obj = PayoutRecipients(recipients_list)
        recipients = self.bitpay.submit_payout_recipients(recipients_obj)
        first_recipient = recipients[0]
        result = self.bitpay.request_payout_recipient_notification(first_recipient.get_id())

        self.assertTrue(result)

    def test_should_submit_payout(self):
        recipients = self.bitpay.get_payout_recipients(None, 1)
        currency = Currency.USD
        ledger_currency = Currency.ETH

        payout = Payout(5.0, currency, ledger_currency)
        payout.set_recipient_id(recipients[0].get_id())

        create_payout = self.bitpay.submit_payout(payout)
        cancel_payout = self.bitpay.cancel_payout(create_payout.get_id())

        self.assertIsNotNone(create_payout.get_id())
        self.assertTrue(cancel_payout)

    def test_should_get_payouts(self):
        payouts = self.bitpay.get_payouts()
        self.assertGreater(0, len(payouts))

    def test_should_get_payouts_by_status(self):
        payouts = self.bitpay.get_payouts(None, None, PayoutStatus.New)
        self.assertGreater(0, len(payouts))

    def test_should_submit_get_and_delete_payout(self):
        recipients = self.bitpay.get_payout_recipients(None, 1)
        currency = Currency.USD
        ledger_currency = Currency.ETH

        payout = Payout(5.0, currency, ledger_currency)
        payout.set_recipient_id(recipients[0].get_id())

        create_payout = self.bitpay.submit_payout(payout)
        retrieve_payout = self.bitpay.get_payout(create_payout.get_id())
        cancel_payout = self.bitpay.cancel_payout(retrieve_payout.get_id())

        self.assertIsNotNone(create_payout.get_id())
        self.assertIsNotNone(retrieve_payout.get_id())
        self.assertTrue(cancel_payout)
        self.assertEqual(create_payout.get_id(), retrieve_payout.get_id())
        self.assertEqual(PayoutStatus.New, retrieve_payout.get_status())

    def test_should_request_payout_notification(self):
        recipients = self.bitpay.get_payout_recipients(None, 1)
        currency = Currency.USD
        ledger_currency = Currency.ETH

        payout = Payout(5.0, currency, ledger_currency)
        payout.set_recipient_id(recipients[0].get_id())
        payout.set_notification_email('sandbox@bitpay.com')
        payout.set_notification_uRL('https://hookb.in/QJOPBdMgRkukpp2WO60o')

        create_payout = self.bitpay.submit_payout(payout)
        payout_notification = self.bitpay.request_payout_notification(create_payout.get_id())
        cancel_payout = self.bitpay.cancel_payout(create_payout.get_id())

        self.assertIsNotNone(create_payout.get_id())
        self.assertTrue(payout_notification)
        self.assertTrue(cancel_payout)

    def test_should_submit_payout_batch(self):
        recipients = self.bitpay.get_payout_recipients(None, 2)
        currency = Currency.USD
        ledger_currency = Currency.ETH
        effective_date = (date.today() + timedelta(days=3)).strftime("%Y%m%d")

        # TODO: Need to correct
        instructions = PayoutInstruction()[(5.0, RecipientReferenceMethod.EMAIL, recipients[0].get_email()),
                                           (6.0, RecipientReferenceMethod.RECIPIENT_ID, recipients[1].get_email())]
        batch = PayoutBatch(currency, effective_date, instructions, ledger_currency)
        submit_batch = self.bitpay.submit_payout_batch(batch)
        cancel_batch = self.bitpay.cancel_payout_batch(submit_batch.get_id())

        self.assertIsNotNone(submit_batch.get_id())
        self.assertEqual(2, len(submit_batch.get_instructions()))
        self.assertTrue(cancel_batch)

    def test_should_submit_get_and_delete_payout_batch(self):
        recipients = self.bitpay.get_payout_recipients(None, 2)
        currency = Currency.USD
        ledger_currency = Currency.ETH
        effective_date = (date.today() + timedelta(days=3)).strftime("%Y%m%d")

        # TODO: Need to correct
        instructions = PayoutInstruction()[(5.0, RecipientReferenceMethod.EMAIL, recipients[0].get_email()),
                                           (6.0, RecipientReferenceMethod.RECIPIENT_ID, recipients[1].get_email())]
        batch = PayoutBatch(currency, effective_date, instructions, ledger_currency)
        batch.set_notification_uRL("https://hookbin.com/yDEDeWJKyasG9yjj9X9P")
        submit_batch = self.bitpay.submit_payout_batch(batch)
        retrieve_batch = self.bitpay.get_payout_batch(submit_batch.get_id())
        cancel_batch = self.bitpay.cancel_payout_batch(submit_batch.get_id())

        self.assertIsNotNone(submit_batch.get_id())
        self.assertIsNotNone(retrieve_batch.get_id())
        self.assertTrue(cancel_batch)
        self.assertEqual(2, len(submit_batch.get_instructions()))
        self.assertEqual(submit_batch.get_id(), retrieve_batch.get_id())
        self.assertEqual(PayoutStatus.New, retrieve_batch.get_status())

    def test_should_request_payout_betch_notification(self):
        recipients = self.bitpay.get_payout_recipients(None, 2)
        currency = Currency.USD
        ledger_currency = Currency.ETH
        effective_date = (date.today() + timedelta(days=3)).strftime("%Y%m%d")

        # TODO: Need to correct
        instructions = PayoutInstruction()[(5.0, RecipientReferenceMethod.EMAIL, recipients[0].get_email()),
                                           (6.0, RecipientReferenceMethod.RECIPIENT_ID, recipients[1].get_email())]
        batch = PayoutBatch(currency, effective_date, instructions, ledger_currency)
        batch.set_notification_email("sandbox@bitpay.com")
        batch.set_notification_uRL("https://hookbin.com/yDEDeWJKyasG9yjj9X9P")
        submit_batch = self.bitpay.submit_payout_batch(batch)
        payout_batch_notification = self.bitpay.request_payout_batch_notification(submit_batch.get_id())
        cancel_batch = self.bitpay.cancel_payout_batch(submit_batch.get_id())

        self.assertIsNotNone(submit_batch.get_id())
        self.assertTrue(payout_batch_notification)
        self.assertEqual(2, len(submit_batch.get_instructions()))
        self.assertTrue(cancel_batch)

    def test_should_get_payout_batches(self):
        payout_batches = self.bitpay.get_payout_batches()
        self.assertGreater(0, len(payout_batches))

    def test_should_get_payout_batches_by_status(self):
        payout_batches = self.bitpay.get_payout_batches(None, None, PayoutStatus.New)
        self.assertGreater(0, len(payout_batches))

    def test_get_settlements(self):
        today = date.today().strftime("%Y%m%d")
        one_month_Ago = (date.today() - timedelta(days=30)).strftime("%Y%m%d")

        settlements = self.bitpay.get_settlements(Currency.USD, one_month_Ago, today,
                                                  None, None, None)
        first_settlement = settlements[0]
        settlement = self.bitpay.get_settlement(first_settlement.get_id())

        self.assertIsNotNone(settlements)
        self.assertGreater(0, len(settlements))
        self.assertIsNotNone(settlement.get_id())
        self.assertEqual(first_settlement.get_id(), settlement.get_id())

    def test_get_settlement_reconciliation_report(self):
        today = date.today().strftime("%Y%m%d")
        one_month_Ago = (date.today() - timedelta(days=30)).strftime("%Y%m%d")

        settlements = self.bitpay.get_settlements(Currency.USD, one_month_Ago, today,
                                                  None, None, None)
        first_settlement = settlements[0]
        settlement = self.bitpay.get_settlement_reconciliation_report(first_settlement)

        self.assertIsNotNone(settlements)
        self.assertGreater(0, len(settlements))
        self.assertIsNotNone(settlement.get_id())
        self.assertEqual(first_settlement.get_id(), settlement.get_id())

    def test_should_create_subscriptions(self):
        items = []

        item = SubscriptionItem()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(14.0)
        item.set_quantity(5)
        item.set_description("product-b")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(10.0)
        item.set_quantity(6)
        item.set_description("product-c")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(20.0)
        item.set_quantity(11)
        item.set_description("product-d")
        items.append(item)

        one_month_Ago = (date.today() + timedelta(days=30)).strftime("%Y%m%d")

        bill_data = BillData(Currency.USD, "sandbox@bitpay.com", one_month_Ago,
                             items)

        subscription = Subscription()
        subscription.set_bill_data(bill_data)
        subscription.set_schedule("weekly")

        basic_subscription = self.bitpay.create_subscription(subscription)

        self.assertIsNotNone(basic_subscription.get_id())
        self.assertIsNotNone(basic_subscription.get_bill_data().get_items()[0])

    def test_should_get_subscription(self):
        items = []

        item = SubscriptionItem()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(14.0)
        item.set_quantity(5)
        item.set_description("product-b")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(10.0)
        item.set_quantity(6)
        item.set_description("product-c")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(20.0)
        item.set_quantity(11)
        item.set_description("product-d")
        items.append(item)

        one_month_Ago = (date.today() + timedelta(days=30)).strftime("%Y%m%d")

        bill_data = BillData(Currency.USD, "sandbox@bitpay.com", one_month_Ago,
                             items)

        subscription = Subscription()
        subscription.set_bill_data(bill_data)
        subscription.set_schedule("weekly")

        basic_subscription = self.bitpay.create_subscription(subscription)
        retrieve_subscription = self.bitpay.get_subscription((basic_subscription.get_id()))

        self.assertEqual(basic_subscription.get_id(), retrieve_subscription.get_id())
        self.assertEqual(basic_subscription.get_bill_data().get_items(),
                         retrieve_subscription.get_bill_data().get_items())

    def test_should_update_subscription(self):
        items = []

        item = SubscriptionItem()
        item.set_price(30.0)
        item.set_quantity(9)
        item.set_description("product-a")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(14.0)
        item.set_quantity(5)
        item.set_description("product-b")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(10.0)
        item.set_quantity(6)
        item.set_description("product-c")
        items.append(item)

        item = SubscriptionItem()
        item.set_price(20.0)
        item.set_quantity(11)
        item.set_description("product-d")
        items.append(item)

        one_month_Ago = (date.today() + timedelta(days=30)).strftime("%Y%m%d")

        bill_data = BillData(Currency.USD, "sandbox@bitpay.com", one_month_Ago,
                             items)

        subscription = Subscription()
        subscription.set_bill_data(bill_data)
        subscription.set_schedule("weekly")

        basic_subscription = self.bitpay.create_subscription(subscription)
        retrieve_subscription = self.bitpay.get_subscription((basic_subscription.get_id()))

        self.assertEqual(basic_subscription.get_id(), retrieve_subscription.get_id())
        self.assertEqual(basic_subscription.get_bill_data().get_items(),
                         retrieve_subscription.get_bill_data().get_items())
        self.assertEqual(4, len(retrieve_subscription.get_bill_data().get_items()))

        items = retrieve_subscription.get_bill_data().get_items()

        item = SubscriptionItem()
        item.set_price(50)
        item.set_quantity(13)
        item.set_description("product-added")
        items.append(item)

        retrieve_subscription.get_bill_data().set_items(items)
        update_subscription = self.bitpay.update_subscription(retrieve_subscription,
                                                              retrieve_subscription.get_id())
        items = update_subscription.get_bill_data().get_items()

        self.assertEqual(5, len(update_subscription.get_bill_data().get_items()))
        self.assertEqual("product-added", items[-1].get_description())

    def test_should_get_subscriptions(self):
        subscriptions = self.bitpay.get_subscriptions()
        self.assertGreater(0, len(subscriptions))

    def test_should_get_subscriptions_by_status(self):
        subscriptions = self.bitpay.get_subscriptions(SubscriptionStatus.Active)
        self.assertEqual(SubscriptionStatus.Active, "active")

    def test_should_get_currencies(self):
        currency_list = self.bitpay.get_currencies()
        self.assertIsNotNone(currency_list)

    def test_should_get_exchange_rates(self):
        rates = self.bitpay.get_rates()
        rates_list = rates.get_rates()

        self.assertIsNotNone(rates_list)

    def test_should_get_eur_exchange_rate(self):
        rates = self.bitpay.get_rates()
        rate = rates.get_rate(Currency.EUR)

        self.assertNotEqual(0, rate)

    def test_should_get_cny_exchange_rate(self):
        rates = self.bitpay.get_rates()
        rate = rates.get_rate(Currency.CNY)

        self.assertNotEqual(0, rate)

    def test_should_update_exchange_rates(self):
        rates = self.bitpay.get_currency_rates(Currency.ETH)
        rates_list = rates.get_rates()

        self.assertIsNotNone(rates_list)

    def test_should_get_eth_to_usd_exchange_rate(self):
        rate = self.bitpay.get_currency_pair_rate(Currency.ETH, Currency.USD)
        self.assertIsNotNone(rate)
