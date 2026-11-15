"""Pandas reference implementation. Fabric implementation uses Spark/Delta notebooks.

Purpose: make transformations inspectable and automatically testable without
claiming that local CSV outputs are Delta Lake tables.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def input_csv(root,name):
    return pd.read_csv(root / f'{name}.csv', dtype={'customer_id':'string','product_id':'string','order_id':'string','order_item_id':'string'})

def prepare(source):
    raw={name:input_csv(source,name) for name in ('customers','products','orders','order_items')}
    c=raw['customers'].drop_duplicates('customer_id',keep='first').copy()
    c['region']=c.region.fillna('').replace('', 'Unknown')
    c['signup_date']=pd.to_datetime(c.signup_date,errors='coerce')
    c=c.dropna(subset=['customer_id','signup_date'])
    p=raw['products'].drop_duplicates('product_id').copy()
    p['list_price']=pd.to_numeric(p.list_price,errors='coerce')
    p=p[p.list_price>0]
    o=raw['orders'].drop_duplicates('order_id').copy()
    o['order_date']=pd.to_datetime(o.order_date,errors='coerce')
    o=o.dropna(subset=['order_date'])
    o=o[o.customer_id.isin(c.customer_id)]
    i=raw['order_items'].drop_duplicates('order_item_id').copy()
    for col in ('quantity','unit_price','discount_pct'):
        i[col]=pd.to_numeric(i[col],errors='coerce')
    i=i[(i.quantity>0)&(i.unit_price>=0)&i.discount_pct.between(0,1)]
    i=i[i.order_id.isin(o.order_id)&i.product_id.isin(p.product_id)].copy()
    i['gross_sales']=(i.quantity*i.unit_price).round(2)
    i['net_sales']=(i.gross_sales*(1-i.discount_pct)).round(2)
    # Order statuses retained in Silver; only Completed counts as realized Gold revenue.
    item_join=(i.merge(o[['order_id','customer_id','order_date','order_status']],on='order_id',validate='many_to_one')
               .merge(p[['product_id','product_name','category']],on='product_id',validate='many_to_one'))
    completed=item_join[item_join.order_status=='Completed'].copy()
    completed['sales_date']=completed.order_date.dt.strftime('%Y-%m-%d')
    completed['year_month']=completed.order_date.dt.strftime('%Y-%m')
    daily=(completed.groupby('sales_date',as_index=False).agg(net_revenue=('net_sales','sum'),units_sold=('quantity','sum'),orders=('order_id','nunique')))
    daily['net_revenue']=daily.net_revenue.round(2)
    products=(completed.groupby(['product_id','product_name','category'],as_index=False).agg(net_revenue=('net_sales','sum'),units_sold=('quantity','sum'),orders=('order_id','nunique')))
    products['net_revenue']=products.net_revenue.round(2)
    cust=(completed.groupby('customer_id',as_index=False).agg(lifetime_revenue=('net_sales','sum'),completed_orders=('order_id','nunique'),last_order_date=('sales_date','max')))
    customer360=(c[['customer_id','customer_name','region']].merge(cust,on='customer_id',how='left',validate='one_to_one'))
    customer360['lifetime_revenue']=customer360.lifetime_revenue.fillna(0).round(2)
    customer360['completed_orders']=customer360.completed_orders.fillna(0).astype(int)
    metrics={'raw_rows':{k:len(v) for k,v in raw.items()},
        'silver_rows':{'customers':len(c),'products':len(p),'orders':len(o),'order_items':len(i)},
        'rejected_items':len(raw['order_items'])-len(i),
        'gold':{'daily_sales_rows':len(daily),'product_rows':len(products),'customer_rows':len(customer360),
        'completed_orders':int(completed.order_id.nunique()), 'net_revenue':round(float(completed.net_sales.sum()),2)},
        'note':'Pandas/CSV reference output, not an executed Fabric or Delta Lake pipeline.'}
    silver={'customers':c,'products':p,'orders':o,'order_items':i}
    gold={'gold_daily_sales':daily,'gold_product_performance':products,'gold_customer_360':customer360}
    return silver,gold,metrics

def main(source:Path,out:Path):
    silver,gold,metrics=prepare(source)
    for layer, tables in [('silver',silver),('gold',gold)]:
        dest=out/layer;dest.mkdir(parents=True,exist_ok=True)
        for name,frame in tables.items():frame.to_csv(dest/f'{name}.csv',index=False)
    (out/'quality_report.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8')
    return metrics

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',default='2-Sample-Retail-Data');ap.add_argument('--output',default='3-Project-Results/local-run')
    a=ap.parse_args();print(json.dumps(main(Path(a.source),Path(a.output)),indent=2))
