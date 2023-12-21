var API_USERS;
var API_USERS_UPDATE;
var LIST_USERS;


function load_user(data, textStatus, jqXHR){
    return $.ajax({
          url:API_USERS_UPDATE,
          type:"GET",
          headers: { 'X-API-KEY': APIKEY },
          contentType:"application/json; charset=utf-8",
          dataType:"json",
          success: function(data){
              USER_DATA = data;
          }
    });
};

function list_users(data, textStatus, jqXHR) {
    return $.ajax({
      url:API_USERS,
      type:"GET",
      headers: { 'X-API-KEY': APIKEY },
      contentType:"application/json; charset=utf-8",
      dataType:"json",
      success: function(data){
          LIST_USERS = data;
      },
    })
};

function empty_callback(data=null, textStatus=null, jqXHR=null){
  return data, textStatus, jqXH
};

function update_profile(payload, callback_model=empty_callback, callback_view=empty_callback){
    $.ajax({
          url:API_USERS_UPDATE + payload['user_id'],
          type:"PUT",
          headers: { 'X-API-KEY': APIKEY },
          contentType:"application/json; charset=utf-8",
          dataType:"json",
          data: JSON.stringify(payload),
          success: function(data){
          },
          error: function(data){
              console.log(data);
          },
          complete: function(data){
          }
    }).then(callback_model).then(callback_view);
};