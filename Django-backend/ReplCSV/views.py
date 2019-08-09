import csv
import pandas as pd
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from.models import stores_static_rank
from django.shortcuts import render

class CSVGenerate(APIView):
    def post(self,request):
        retailer = request.POST.get('Retailer')
        if retailer:
            try:
                bsqreader = csv.DictReader(request.FILES['bsq'].read().decode("utf-8").splitlines())
                storedf = pd.read_csv(request.FILES['store'])
                warehousedf = pd.read_csv(request.FILES['warehouse'])
            except Exception as e:
                return Response({"Message": str(e) + " Parameter is Required"}, status=status.HTTP_400_BAD_REQUEST)
            quantlist = []
            for i in bsqreader:
                prod,stor,bsqval = i['Product_Code'],i['Store_Code'],int(i['BSQ'])
                storeinvdf = storedf.loc[(storedf.Product_Code == prod) & (storedf.Store_Code == stor),'Closing_Inventory']
                if not storeinvdf.empty:

                    storeinv = int(storeinvdf.values[0]) if int(storeinvdf.values[0])>=0 else None
                    if storeinv and storeinv < bsqval and bsqval>=0:
                        req_qty = bsqval - storeinv
                        dict = {"Product_Code":prod,"Store_Code":stor,"Req_qty":req_qty}
                        quantlist.append(dict)

            quantlist = pd.DataFrame(quantlist)
            req_qty_sum = quantlist.groupby('Product_Code').apply(lambda x: sum(x['Req_qty'].unique()))
            quantlist['Warehouse'] = ""
            for i in req_qty_sum.index.tolist():
                df = warehousedf.loc[warehousedf.Product_Code == i, ['WH_Qty','WH']]
                if not df.empty:
                    req = int(req_qty_sum.loc[i])
                    wh_qty = int(df.iloc[0]['WH_Qty'])
                    if req <= wh_qty:
                        quantlist.loc[quantlist.Product_Code == i, 'Warehouse'] = df.iloc[0]['WH']
                    else:
                        rank = stores_static_rank.objects.all().order_by('Static_Priority')
                        val = wh_qty
                        for j in rank:
                            temdf = quantlist.loc[
                                (quantlist.Product_Code == i) & (
                                            quantlist.Store_Code == j.Store_Code), 'Req_qty'].values
                            if temdf:
                                qty = int(temdf[0])
                                quantlist.loc[(quantlist.Product_Code == i) & (
                                        quantlist.Store_Code == j.Store_Code), 'Warehouse'] = df.iloc[0]['WH']
                                if qty <= val:
                                    val = val - qty
                                else:
                                    quantlist.loc[(quantlist.Product_Code == i) & (
                                        quantlist.Store_Code == j.Store_Code), 'Req_qty'] = "Out Of Stock"
                else:
                    quantlist.loc[(quantlist.Product_Code == i) , 'Req_qty'] = "WH inventory missing"

            quantlist.rename(columns={'Req_qty': 'Replenishment_Qty','Warehouse':'From_Warehouse_id','Store_Code':'To_Store_id','Product_Code':'Product/SKU'},inplace=True)
            order = ['From_Warehouse_id','To_Store_id','Product/SKU','Replenishment_Qty']
            quantlist = quantlist[order]
            response = HttpResponse(quantlist.to_csv(index=False), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="ReplinshmentOrder.csv"'
            return response
        else:
            return Response({"Message" : "Unauthorized Retailer"},status=status.HTTP_401_UNAUTHORIZED)

    def get(self,request):
        return render(request, "index.html")



