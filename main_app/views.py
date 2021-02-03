from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate,login,logout
from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)
from main_app.models import DataSource, Document
from main_app.forms import UserForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse_lazy
import requests
import csv
import re
import json

data_mos_api = {
                'NAME':'data.mos.ru',
                'KEY':'?api_key=59d8adf705de7834a39f87457243b462',
                'URL':'https://apidata.mos.ru/v1/datasets',
                'FILTER':'&$filter=CategoryId eq 6',
                'PARAM':'&rows'
                }

data_gov_api = {
                'NAME':'data.gov.ru',
                'KEY':'?access_token=5db3b39d3e9c0938c15c729cef991461',
                'URL':'https://data.gov.ru/api/json/dataset',
                'FILTER':'&topic=Education',
                }

SOURCE = {
    'data_mos':'data.mos.ru',
    'data_gov':'data.gov.ru',
    'obrnadzor':'obrnadzor.gov.ru'
}

class DataSourceListView(ListView):
    model = DataSource
    context_object_name = 'sources_list'
    queryset = DataSource.objects.all().order_by('-edit_date')
    template_name = 'main_app/sources.html'

class  DataSourceDetailView(DetailView):
    model =  DataSource

class DataSourceDeleteView(LoginRequiredMixin,DeleteView):
    model = DataSource

    success_url = reverse_lazy('sources')

class DataSourceCreateView(LoginRequiredMixin, generic.CreateView):
    model = DataSource
    fields = ('url',)
    template_name = 'main_app/sources_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.edit_date = timezone.now()
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('sources')


def register(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request,'registration/registration.html',
        {'user_form': user_form,
        'registered':registered,
        })

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                print('user: {} login'.format(username))
                return reverse_lazy('main')
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("LOgIN AND FAIL")
            print("Username:{} and password:{}".format(username,password))
            return HttpResponse('invalid login details')
    else:
        return render(request,'registration/login.html',{})

def search_in(search, caption):
    if search == '':
        return False

    pattern = r'{word}'.format(word=search)
    if re.search(pattern, caption) != None:
        return True
    return False

def data_mos(search):

    documents = []
   
    print(data_mos_api['URL']+data_mos_api['KEY']+data_mos_api['FILTER'])

    response = requests.get(data_mos_api['URL']+data_mos_api['KEY']+data_mos_api['FILTER'])

    if response.status_code != 200:
        documents.append("error")
        documents.append(str(response.status_code))
        return documents

    loaded_json = json.loads(response.text)

    for doc in loaded_json:
        formatted_doc = {
            'Caption': doc['Caption'],
            'Id': doc['Id'],
            'Description': doc['FullDescription'],
            'Keywords': doc['Keywords'],
            'Department': doc['DepartmentId']
        }

        if search == '':
            documents.append(formatted_doc)
        elif search_in(search, formatted_doc['Caption']):
            documents.append(formatted_doc)
    return documents

def data_gov(search):

    documents = []

    print(data_gov_api['URL']+data_gov_api['KEY']+data_gov_api['FILTER'])

    response = requests.get(data_gov_api['URL']+data_gov_api['KEY']+data_gov_api['FILTER'])

    if response.status_code != 200:
        documents.append("error")
        documents.append(str(response.status_code))
        return documents

    loaded_json = json.loads(response.text)

    for doc in loaded_json:
        formatted_doc = {
            'Caption': doc['title'],
            'Id': doc['identifier']
        }
        if search == '':
            documents.append(formatted_doc)
        elif search_in(search, formatted_doc['Caption']):
            documents.append(formatted_doc)

    return documents

def obrnadzor(search):

    documents = []
    db_documents = Document.objects.all()

    for doc in db_documents:
        formatted_doc = {
            'Caption': doc.Caption,
            'Id': doc.DocId
        }
        if search == '':
            documents.append(formatted_doc)
        elif search_in(search, formatted_doc['Caption']):
            documents.append(formatted_doc)

    return documents

def data_gov_preview(request, id):
    response_version = requests.get(data_gov_api['URL']+'/'+str(id)+'/version'+data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+'/version'+data_gov_api['KEY'])
    loaded_json_version = json.loads(response_version.text)
    
    first_version_in_list = loaded_json_version[0]['created']
    
    # https://data.gov.ru/api/json/dataset/7710539135-trud/version?access_token=5db3b39d3e9c0938c15c729cef991461
    # then get link to csv file version

    response_version_info = requests.get(data_gov_api['URL']+'/'+str(id)+'/version'+'/'+first_version_in_list+data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+'/version'+'/'+first_version_in_list+data_gov_api['KEY'])
    loaded_json_version_info = json.loads(response_version_info.text)


    if len(loaded_json_version_info) == 0:
        #loaded_json.update({'empty':"true"})
        return HttpResponse(json.dumps(loaded_json_version_info), content_type='application/json')
    
    print(loaded_json_version_info[0])


    # https://data.gov.ru/api/json/dataset/7710539135-trud/version/20190204T093242/content?access_token=5db3b39d3e9c0938c15c729cef991461

    response_content = requests.get(data_gov_api['URL']+'/'+str(id)+'/version/'+ loaded_json_version_info[0]['created'] + '/content' + data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+'/version/'+ loaded_json_version_info[0]['created'] + '/content' + data_gov_api['KEY'])
    loaded_json_content = json.loads(response_content.text)

    print(loaded_json_content)

    return HttpResponse(json.dumps(loaded_json_content), content_type='application/json')

def gov_details(request, id):

    # https://data.gov.ru/api/json/dataset/7710539135-DO?access_token=5db3b39d3e9c0938c15c729cef991461

    response = requests.get(data_gov_api['URL']+'/'+str(id)+data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+data_gov_api['KEY'])

    loaded_json = json.loads(response.text)
    print(loaded_json)


     # load versions 
    # https://data.gov.ru/api/json/dataset/7710539135-trud/version?access_token=5db3b39d3e9c0938c15c729cef991461

    response_version = requests.get(data_gov_api['URL']+'/'+str(id)+'/version'+data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+'/version'+data_gov_api['KEY'])
    loaded_json_version = json.loads(response_version.text)
    
    first_version_in_list = loaded_json_version[0]['created']
    
    # https://data.gov.ru/api/json/dataset/7710539135-trud/version?access_token=5db3b39d3e9c0938c15c729cef991461
    # then get link to csv file version

    response_version_info = requests.get(data_gov_api['URL']+'/'+str(id)+'/version'+'/'+first_version_in_list+data_gov_api['KEY'])
    print(data_gov_api['URL']+'/'+str(id)+'/version'+'/'+first_version_in_list+data_gov_api['KEY'])
    loaded_json_version_info = json.loads(response_version_info.text)

    if len(loaded_json_version_info) == 0:
        loaded_json.update({'file_url':""})
        return HttpResponse(json.dumps(loaded_json), content_type='application/json')
    

    loaded_json.update({'version':loaded_json_version_info[0]})

    print(loaded_json_version_info)
    file_url = loaded_json_version_info[0]['source']

    loaded_json.update({'file_url':file_url})
    

    return HttpResponse(json.dumps(loaded_json), content_type='application/json')

def mos_details(request, id):

    # https://apidata.mos.ru/v1/datasets/562?api_key=59d8adf705de7834a39f87457243b462

    response = requests.get(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    print(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    
    loaded_json = json.loads(response.text)
    print(loaded_json)

    return HttpResponse(json.dumps(loaded_json), content_type='application/json')

def obrnadzor_details(request, id):
    docs = Document.objects.filter(DocId=id)
    doc = docs[0]
    formatted_doc = {
        'description': doc.Description,
        'departmentCaption': doc.Department,
        'keywords': doc.Keywords,
        'file_url': doc.file_url,
    }
  
    return HttpResponse(json.dumps(formatted_doc), content_type='application/json')

def mos_rows(request, id):

    # https://apidata.mos.ru/v1/datasets/562/rows?api_key=59d8adf705de7834a39f87457243b462

    response = requests.get(data_mos_api['URL']+'/'+str(id)+'/rows'+data_mos_api['KEY'])
    print(data_mos_api['URL']+'/'+str(id)+'/rows'+data_mos_api['KEY'])
    
    loaded_json = json.loads(response.text)
    print(loaded_json)

    return HttpResponse(json.dumps(loaded_json), content_type='application/json')

def mos_download(request, id):

    # Тип ответа - csv файл
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_mos.csv"'

    writer = csv.writer(response)

    # Запрос для заголовков
    # https://apidata.mos.ru/v1/datasets/562?api_key=59d8adf705de7834a39f87457243b462
    mos_details = requests.get(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    print(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    loaded_json = json.loads(mos_details.text)

    # writer.writerow(loaded_json["Columns"])
    row_list = []
    for item in loaded_json["Columns"]:
        row_list.append(item["Caption"])
    writer.writerow(row_list)
    
    # Запрос для строк
    # https://apidata.mos.ru/v1/datasets/562/rows?api_key=59d8adf705de7834a39f87457243b462
    mos_rows = requests.get(data_mos_api['URL']+'/'+str(id)+'/rows'+data_mos_api['KEY'])
    print(data_mos_api['URL']+'/'+str(id)+'/rows'+data_mos_api['KEY'])
    loaded_json = json.loads(mos_rows.text)

    for item in loaded_json:
        row_list = []
        for key in item["Cells"]:
            row_list.append(item["Cells"][key])
        writer.writerow(row_list)

    return response


def row_info(request, id):

    response = requests.get(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    print(data_mos_api['URL']+'/'+str(id)+data_mos_api['KEY'])
    loaded_json = json.loads(response.text)


    print(loaded_json)

    return HttpResponse(json.dumps(loaded_json), content_type='application/json')


    # if request.is_ajax():
    #     print("ajax")
    #     data = {"msg":"msg_info", "id":id}
    #     # Do somw staff to get api req for complex info
    #     return HttpResponse(json.dumps(data), content_type='application/json')
    # else:
    #     print("none ajax")
    #     data = {"msg":"msg_info", "id":id}
    #     return HttpResponse(json.dumps(data), content_type='application/json')


def index(request):

    search=''

    if request.method == "POST":
        search = request.POST['search']

    print(search)

    
    data_mos_data = data_mos(search)
    data_mos_title = SOURCE['data_mos']

    data_gov_data = data_gov(search)
    data_gov_title = SOURCE['data_gov']

    obrnadzor_data = obrnadzor(search)
    obrnadzor_title = SOURCE['obrnadzor']

    if data_mos_data != [] and data_mos_data[0] == "error":
        data_mos_title = data_mos_title + " - " +  data_mos_data[0] + " " +  data_mos_data[1] + " service unavalible"
        data_mos_data = []

    if data_gov_data != [] and data_gov_data[0] == "error":
        data_gov_title = data_gov_title + " - " +  data_gov_data[0] + " " +  data_gov_data[1] + " service unavalible"
        data_gov_data = []

    if obrnadzor_data != [] and obrnadzor_data[0] == "error":
        obrnadzor_title = obrnadzor_title + " - " +  obrnadzor_data[0] + " " +  obrnadzor_data[1] + " service unavalible"
        obrnadzor_data = []


    data = {
        'context_data':'Введите имя интересующего документа',
        'search_query': search,
        'source_list' : [
            {
            'source': data_mos_title,
            'id':'data-mos',
            'document_list': data_mos_data
            # 'document_list': [
            #     { 'Caption':'Документ1 data_mos_ru'},
            #     { 'Caption':'Документ2 data_mos_ru'},
            #     { 'Caption':'Документ3 data_mos_ru'},
            # ]
            },
            {
            'source':data_gov_title,
            'id':'data-gov',
            'document_list': data_gov_data
            # 'document_list': [
            #     { 'Caption':'Документ1 data_gov_ru'},
            #     { 'Caption':'Документ2 data_gov_ru'},
            #     { 'Caption':'Документ3 data_gov_ru'},
            # ]
            },
            {
            'source':obrnadzor_title,
            'id':'source-3',
            'document_list': obrnadzor_data
            },
        ]
    }

    if search != '':
        print("search!")

    return render(request, 'main_app/index.html', context=data)

