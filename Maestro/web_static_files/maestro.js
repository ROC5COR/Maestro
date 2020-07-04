application_created_by_name = []

function update_server_list() {
    console.log('Updating server list');
    $.get("server_list", function(data, status){
        let list = document.createElement('ul');
        data.forEach(server_object => {
            let item = document.createElement('li');
            item.appendChild(document.createTextNode(server_object['name']+
                ' v'+server_object['version']+' on '+
                server_object['source']+':'+server_object['port']));
            list.appendChild(item);
        });
        $("#server_list").html(list);
    });
}

function update_application_list() {
    console.log('Updating application list');
    $.get("application_list", function(data, status){
        let list = document.createElement('ul');
        data.forEach(app_info => {
            let item = document.createElement('li');
            item.appendChild(document.createTextNode(app_info['name']+
                ': '+app_info['status']));
            list.appendChild(item);

            if(!application_created_by_name.includes(app_info['uuid'])){
                let div = document.createElement('div');
                div.setAttribute("id", app_info['uuid']);
                div.setAttribute("class", "scenario_box col-5");

                let box_title = document.createElement('div');
                box_title.setAttribute('class','data_title');
                div.setAttribute("onclick", "update_scenario_data_box(\""+app_info['uuid']+"\");")
                box_title.appendChild(document.createTextNode(app_info['name']));
                div.appendChild(box_title);

                let variables_title = document.createElement('div');
                variables_title.setAttribute('class','data_title');
                variables_title.appendChild(document.createTextNode("Variables:"));
                div.appendChild(variables_title);

                let variablesDiv = document.createElement('div');
                variablesDiv.setAttribute('class','data_text');
                variablesDiv.setAttribute('id',app_info['uuid']+'-variables');
                div.appendChild(variablesDiv);

                $("#applications_div").append(div);
                application_created_by_name.push(app_info['uuid'])
            }

        });
        $("#application_list").html(list);
    });
}

function createImageDataObjectFromData(img_data, img_format){
    let img = document.createElement('img');
    img.setAttribute('style','max-width:100%');
    img.setAttribute('src', 'data:image/'+img_format+';base64,'+img_data);
    let imgDiv = document.createElement('div');
    imgDiv.appendChild(img);
    return imgDiv;
}

function update_scenario_data_box(uuid) {
    $.get("applications/"+uuid+"/variables", function(data, status){
        let list = document.createElement('ul');
        console.log(data);
        Object.keys(data).forEach((e) => {
            let elem = document.createElement('li');
            if(data[e] == null){
                elem.appendChild(document.createTextNode(e + " : Data is null"));
            }
            else if(data[e] instanceof String){
                console.log(data[e])
            } else if(data[e] instanceof Array){
                // Assuming array of object
                data[e].forEach( obj => {
                    if(obj['type'] == 'plain/text'){
                        elem.appendChild(document.createTextNode(e + " : " + obj['data']));
                    } else if(obj['type'] == 'image/png'){
                        elem.appendChild(createImageDataObjectFromData(obj['data'], 'png'));
                    } else if(obj['type'] == 'image/jpg'){
                        elem.appendChild(createImageDataObjectFromData(obj['data'], 'jpg'));
                    } else {
                        console.log("Don't know how to display data of type: "+obj['type']);
                    }
                });
            } else if(data[e] instanceof Object){
                //Assumin direct object with data and type key
                if(data[e]['type'] == 'plain/text'){
                    elem.appendChild(document.createTextNode(e + " : " + data[e]['data']));
                } else if(data[e]['type'] == 'image/png'){
                    elem.appendChild(createImageDataObjectFromData(data[e]['data']));
                }
            } else {
                elem.appendChild(document.createTextNode(e + " : [Can't decode this type of data]"));
            }
            list.appendChild(elem);
        });
        console.log(data);
        $("#"+uuid+"-variables").html(list);
    });
}


update_server_list();
update_application_list();
window.setInterval(function() {
    update_server_list();
    update_application_list();
}, 5000);


