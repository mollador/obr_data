function init(){
  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })
}

function load_preview(source, id, parentElem) {
  if (source == "data.mos.ru") {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        respObj = JSON.parse(this.response)

        table_create(parentElem, respObj.Columns)
        load_rows(source, id, parentElem)

        //table_rows(parentElem + '-table', rows, respObj.Columns.length)
      }
    };
    xhttp.open("GET", location.href + "data_mos_details/" + id, true);
    xhttp.send();
  }

  if (source == "data.gov.ru") {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        respObj = JSON.parse(this.response)


        ///----------------------------------HERE----------------------
        //table_create(parentElem, respObj.Columns)
        table_create_data_gov(parentElem, respObj[0])
        table_rows_data_gov(parentElem, respObj)
        //table_rows(parentElem + '-table', rows, respObj.Columns.length)

        ///----------------------------------HERE----------------------
      }
    };
    xhttp.open("GET", location.href + "data_gov_preview/" + id, true);
    xhttp.send();
  }
}

function table_create(parentElem, columns) {
  var parent = document.getElementById(parentElem);
  var tbl = document.createElement('table');
  tbl.style.width = '100%';
  tbl.setAttribute('border', '1');
  tbl.classList.add('my-table');
  tbl.setAttribute("id", parentElem + "-table");
  var tbdy = document.createElement('thead');
  var tr = document.createElement('tr');
    for (var j = 0; j < columns.length; j++) {
      var td = document.createElement('td');
      td.textContent = columns[j].Caption
      tr.appendChild(td)
    }
    tbdy.appendChild(tr);
  tbl.appendChild(tbdy);
  parent.appendChild(tbl)
}

function load_rows(source, id, parentElem) {
  if (source == "data.mos.ru") {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        respObj = JSON.parse(this.response)

        table_rows(parentElem + '-table', respObj)
      }
    };
    xhttp.open("GET", location.href + "data_mos_rows/" + id, true);
    xhttp.send();
  }
}

function table_rows(table_id, rows) {
  var tbl = document.getElementById(table_id);
  var tbdy = document.createElement('tbody');

  console.log(table_id)

  var len = rows.length;
  if (rows.length > 10){
    len = 10;
  }

  for (var i = 0; i < len; i++) {
    var tr = document.createElement('tr');

    for (var key in rows[i].Cells) {
      var td = document.createElement('td');
      td.textContent = rows[i].Cells[key]
      tr.appendChild(td)
    }
    tbdy.appendChild(tr);
  }
  tbl.appendChild(tbdy);
}

function table_create_data_gov(parentElem, columns) {
  var parent = document.getElementById(parentElem);
  var tbl = document.createElement('table');
  tbl.style.width = '100%';
  tbl.setAttribute('border', '1');
  tbl.classList.add('my-table');
  tbl.setAttribute("id", parentElem + "-table");
  var tbdy = document.createElement('thead');
  var tr = document.createElement('tr');
    for (var key in columns) {
      var td = document.createElement('td');
      td.textContent = key
      tr.appendChild(td)
    }
    tbdy.appendChild(tr);
  tbl.appendChild(tbdy);
  parent.appendChild(tbl)
}

function table_rows_data_gov(table_id, rows) {
  var tbl = document.getElementById(table_id+'-table');
  var tbdy = document.createElement('tbody');

  console.log(table_id)

  var len = rows.length;
  if (rows.length > 10){
    len = 10;
  }

  for (var i = 0; i < len; i++) {
    var tr = document.createElement('tr');

    for (var key in rows[i]) {
      var td = document.createElement('td');
      td.textContent = rows[i][key]
      tr.appendChild(td)
    }
    tbdy.appendChild(tr);
  }
  tbl.appendChild(tbdy);
}

function load_data_mos_detail(id, description, department, keywords) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {

        respObj = JSON.parse(this.response)
        document.getElementById(description).innerHTML = respObj["Description"]
        document.getElementById(department).innerHTML = respObj["DepartmentCaption"]
        document.getElementById(keywords).innerHTML = respObj["Keywords"]
      }
    };
    xhttp.open("GET", location.href + "data_mos_details/" + id, true);
    xhttp.send();
}

function load_data_gov_detail(id, description, department, keywords, url) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

      respObj = JSON.parse(this.response)
      document.getElementById(description).innerHTML = respObj["description"]
      document.getElementById(department).innerHTML = respObj["creator"]
      document.getElementById(keywords).innerHTML = respObj["subject"]
      var download = document.getElementById(url);
      download.setAttribute('href', respObj['file_url']);
    }
  };
  xhttp.open("GET", location.href + "data_gov_details/" + id, true);
  xhttp.send();
}



function load_data_detail(source, id, description, department, keywords, url) {
  if (source == "data.mos.ru") {
    var xhttp = new XMLHttpRequest();
    xhttp.timeout = 3000; // time in milliseconds
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

      respObj = JSON.parse(this.response)
      document.getElementById(description).innerHTML = respObj["Description"]
      document.getElementById(department).innerHTML = respObj["DepartmentCaption"]
      document.getElementById(keywords).innerHTML = respObj["Keywords"]
      var download = document.getElementById(url);
      download.innerHTML = "Загрузить набор данных"
      // download.setAttribute('href', respObj['file_url']);
    }
  };
  xhttp.ontimeout = function () {
    document.getElementById(description).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(department).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(keywords).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(url).innerHTML = "LOADING ERROR - NO DATA"
  };
  xhttp.open("GET", location.href + "data_mos_details/" + id, true);
  xhttp.send();
  }

  if (source == "data.gov.ru"){
    var xhttp = new XMLHttpRequest();
    xhttp.timeout = 3000; // time in milliseconds
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      respObj = JSON.parse(this.response)
      document.getElementById(description).innerHTML = respObj["description"]
      document.getElementById(department).innerHTML = respObj["creator"]
      document.getElementById(keywords).innerHTML = respObj["subject"]
      var download = document.getElementById(url);
      if (respObj['file_url'] != "") {
        download.innerHTML = "Загрузить набор данных";
        download.setAttribute('href', respObj['file_url']);
      } else {
        download.innerHTML = "Загрузка недоступна"
      }
    }
  };
  xhttp.ontimeout = function () {
    document.getElementById(description).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(department).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(keywords).innerHTML = "LOADING ERROR - NO DATA"
    document.getElementById(url).innerHTML = "LOADING ERROR - NO DATA"
  };
  xhttp.open("GET", location.href + "data_gov_details/" + id, true);
  xhttp.send();
  }

  if (source == "obrnadzor.gov.ru"){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      respObj = JSON.parse(this.response)
      document.getElementById(description).innerHTML = respObj["description"]
      document.getElementById(department).innerHTML = respObj["departmentCaption"]
      document.getElementById(keywords).innerHTML = respObj["keywords"]
      var download = document.getElementById(url);
      if (respObj['file_url'] != "") {
        download.innerHTML = "Загрузить набор данных";
        download.setAttribute('href', respObj['file_url']);
      } else {
        download.innerHTML = "Загрузка недоступна"
      }
    }
  };
  xhttp.open("GET", location.href + "obrnadzor_details/" + id, true);
  xhttp.send();
  }
}


function del_button(id) {
  document.getElementById(id).remove();
}

