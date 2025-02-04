from django.http import JsonResponse
from . import models
import random, json
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF
from datetime import datetime, timedelta

font_path = "D:\\Github\\foodcom\\foodcom_backend\\telegram-bot\\myfile.ttf"
directory_path = "D:\\Github\\foodcom\\foodcom_backend\\telegram-bot\\docs"

event_types = (
    ('wedding', '가족 개인행사'),
    ('business', '기업 이벤트'),
    ('public', '사회 단체행사'),
    ('festival', '기관, 축제등'),
    ('birthday', '스몰웨딩, 야외결혼'),
    ('steak', '스테이크 행사'),
    ('fingerFood', '핑거푸드')
)

event_places = (
    ('실내', '실내'),
    ('야외', '야외'),
    ('체육관', '체육관'),
    ('연회장', '연회장'),
    ('호텔', '호텔'),
    ('미정', '미정')
)


@api_view(['GET'])
def api(request):
    return Response({"message": "Welcome to the API"})


class LatestCustomerSerializer(models.CustomerSerializer):
    class Meta:
        model = models.Customer
        fields = ('ticket_number', 'name', 'address')

class CustomerViewAPIView(generics.RetrieveAPIView):
    queryset = models.Customer.objects.all()
    serializer_class = models.CustomerSerializer
    lookup_field = 'ticket_number'

class LatestCustomers(generics.ListAPIView):
    queryset = models.Customer.objects.all().order_by('-id')[:10]
    serializer_class = LatestCustomerSerializer

class PDF(FPDF):
    def header(self):
        self.add_font('nanumgothic', '', font_path, uni=True)
        self.set_font('nanumgothic', '', 15)
        page_width = self.w
        header_cell_width = 50
        x = (page_width - header_cell_width) / 2
        self.set_xy(x, 10)
        self.cell(header_cell_width, 10, '푸드컴 확인서', 1, 0, 'C')
        self.ln(10)

@api_view(['GET'])
def generatePDF(request, ticket_number):
    data = models.Customer.objects.get(ticket_number=ticket_number)
    
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('nanumgothic', '', 20)

    line_spacing = 5

    pdf.set_draw_color(0, 0, 0)
    pdf.rect(10, 10, pdf.w - 20, pdf.h - 20) 

    border_height = pdf.h - 100
    border_width = pdf.w - 40
    total_data_height = 12 * 12  

    y = (border_height - total_data_height) / 2 + 10

    pdf.set_xy(20, y)

    tool_data = data.tool

    event = ""
    for event_type in event_types:
        if event_type[0] == data.event_type:
            event = event_type[1]
            break

    if data.event_place == None:
        data.event_place = ""

    if data.event_type == None:
        data.event_type = ""

    if data.custom_tool == None:
        data.custom_tool = ""

    if data.custom_event_place == None:
        data.custom_event_place = ""

    if data.custom_event_type == None:
        data.custom_event_type = ""

    pdf.multi_cell(border_width, 10,
                                      f"고객 이름: {data.name}\n\n"
                                      f"고객 전화 번호: {data.phone_number}\n\n"
                                      f"이벤트 유형: {event} {data.custom_event_type}\n\n"
                                      f"사람 수: {data.people_count}명\n\n"
                                      f"식사비: {data.meal_cost}원\n\n"
                                      f"행사 장소: {data.event_place} {data.custom_event_place}\n\n"
                                      f"주소: {data.address}\n\n"
                                      f"추가: {tool_data}, {data.custom_tool}\n\n"
                                      f"개최 날짜: {data.event_date}\n\n"                                      
                                      f"고객 등록 날짜: {data.date_registered}\n\n"
                                      f"티켓 번호: {data.ticket_number}",
                   align='C')


    pdf_file = f"{directory_path}/{data.name}.pdf"
    pdf.output(pdf_file, 'F')
    return Response({"message" : f"{data.name}.pdf is created in the documents folder"})

@api_view(['GET'])
def new_customer(request):
    all_customers = models.Customer.objects.values()
    all_tickets = []

    for k in all_customers:
        all_tickets.append(k['ticket_number'])

    while True:
        ticket_number = random.randint(1, 100000000)
        if ticket_number not in all_tickets:
            models.Customer.objects.create(name=request.GET.get('name'), address=request.GET.get('address'), \
                                        phone_number=request.GET.get('phone_number'), ticket_number=ticket_number)
        break
    return Response({'ticket_number' : ticket_number})


@csrf_exempt
def process_data(request, ticket_number):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_type = data['event_type']
            event_type_choices = [choice[0] for choice in models.event_types]
            event_place = data['event_place']
            event_place_choices = [choice[0] for choice in models.event_places]
            message = ""

            tool = data['tool']
            numeric_tool = []

            for value in tool:
                numeric_tool.append(int(value))

            people_count = data['people_count']

            if isinstance(people_count, str):
                people_count = int(people_count)
        
            customer = models.Customer.objects.get(ticket_number=ticket_number)
            customer.name = data['name']
            customer.address = data['address']
            customer.phone_number = data['phone_number']
            customer.message = data['message']
            if event_type in event_type_choices:
                message += "Custom event type\n"
                customer.event_type = data['event_type']
            else:
                customer.custom_event_type = data['event_type']

            if event_place in event_place_choices:
                message += "Custom event place\n"
                customer.event_place = data['event_place']
            else:
                customer.custom_event_place = data['event_place']
            customer.people_count = people_count
            event_date = data['event_date']
            event_time = data['event_time']
            customer.event_date = (datetime.strptime(event_date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(hour=0, minute=0) + timedelta(hours=int(event_time.split(":")[0]), minutes=int(event_time.split(":")[1]))).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            customer.meal_cost = data['meal_cost']
            customer.date_registered = datetime.now()
            customer.tool = numeric_tool
            customer.custom_tool = data['customTool']
            customer.ticket_number = ticket_number

            try:
                customer.save()
                print("Customer saved")
            except Exception as e:
                message += str(e) + "\n"
                print(e)

            response_data = {
                'message' : message
            }
            return JsonResponse(response_data)
        except Exception as e:
            print(e)
            return JsonResponse({'error' : str(e)})