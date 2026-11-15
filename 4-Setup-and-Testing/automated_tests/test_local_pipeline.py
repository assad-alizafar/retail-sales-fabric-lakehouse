from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from local_python.generate_demo_data import generate
from local_python.run_local_demo import prepare,main

@pytest.fixture()
def prepared(tmp_path):
    source=tmp_path/'source'
    generate(source,customers_count=50,orders_count=150,seed=42)
    silver,gold,metrics=prepare(source)
    return silver,gold,metrics

def test_customer_deduplication_and_missing_region(prepared):
    silver,_,metrics=prepared
    assert silver['customers'].customer_id.is_unique
    assert 'Unknown' in silver['customers'].region.values
    assert metrics['silver_rows']['customers']==50

def test_invalid_items_rejected(prepared):
    silver,_,metrics=prepared
    assert metrics['rejected_items']>=3
    assert (silver['order_items'].quantity>0).all()
    assert 'P999' not in set(silver['order_items'].product_id)
    assert silver['order_items'].order_item_id.is_unique

def test_gold_revenue_reconciles(prepared):
    _,gold,metrics=prepared
    assert round(gold['gold_daily_sales'].net_revenue.sum(),2)==metrics['gold']['net_revenue']
    assert round(gold['gold_product_performance'].net_revenue.sum(),2)==metrics['gold']['net_revenue']
    assert round(gold['gold_customer_360'].lifetime_revenue.sum(),2)==metrics['gold']['net_revenue']

def test_zero_order_customers_retained(prepared):
    _,gold,metrics=prepared
    assert len(gold['gold_customer_360'])==50
    assert (gold['gold_customer_360'].completed_orders>=0).all()

def test_deterministic_runs(tmp_path):
    source=tmp_path/'source';generate(source,50,150,seed=42)
    a=main(source,tmp_path/'run_a');b=main(source,tmp_path/'run_b')
    assert a==b

def test_no_cancelled_or_returned_orders_counted(prepared):
    silver,gold,metrics=prepared
    eligible=set(silver['orders'].loc[silver['orders'].order_status=='Completed','order_id'])
    assert metrics['gold']['completed_orders']<=len(eligible)
