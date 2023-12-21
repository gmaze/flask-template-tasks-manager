var API_PLANS;
var LIST_OF_PLANS;

function load_plans(){
    return $.ajax({
          url:API_PLANS,
          type:"GET",
          headers: { 'X-API-KEY': APIKEY },
          contentType:"application/json; charset=utf-8",
          dataType:"json",
          success: function(data){
              LIST_OF_PLANS = data;
          }
    });
}

get_html_plan_btn = function(user_data){
    let user_plan = user_data['subscription_plan'];
    html = "<div class='btn-group rounded-3' role='group' aria-label='Subscription plan for user #"+user_data['id']+"'>";
    let color;
    for (let i = 0; i < LIST_OF_PLANS.length; i++) {

        if (LIST_OF_PLANS[i]['level'] == 0) {
            color = ["secondary", "white"];
        } else if (LIST_OF_PLANS[i]['level'] <= 50) {
            color = ["success", "white"];
        } else if (LIST_OF_PLANS[i]['level'] <= 100) {
            color = ["info", "white"];
        } else {
            color = ["light", "dark"];
        }

        html += "<button type='button' class='btn btn-sm btn-outline-"+color[0];
        if (user_plan['label'] === LIST_OF_PLANS[i]['label']) {
            html += " active' aria-pressed='true'>";
        } else {
            html += "' aria-pressed='false'>";
        }
        html += LIST_OF_PLANS[i]['label'];
        html += "</button>";
    }
    return html
}