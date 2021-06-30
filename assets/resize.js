// SOURCE: https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-oil-and-gas/assets/resizing_script.js

if (!window.dash_clientside) {
  window.dash_clientside = {};
}
window.dash_clientside.clientside = {
  resize: function(value) {
    console.log("resizing..."); // for testing
    setTimeout(function() {
      window.dispatchEvent(new Event("resize"));
      console.log("fired resize");
    }, 500);
    return null;
  }
};