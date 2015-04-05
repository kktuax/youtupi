Storage.prototype.setObj = function(key, obj) {
    return this.setItem(key, JSON.stringify(obj))
}
Storage.prototype.getObj = function(key) {
    return JSON.parse(this.getItem(key))
}

function supports_html5_storage() {
	try {
		return 'localStorage' in window && window['localStorage'] !== null;
	} catch (e) {
		return false;
	}
}

function addLocalStorageFor(select, key){
	if(supports_html5_storage()){
		var oldValue = localStorage.getItem(key);
		if(oldValue){
			$(select).val(oldValue);
		}
		$(select).bind("change", function(event, ui) {
			localStorage.setItem(key, $(select).val());
		});
		return true;
	}else{
		return false;
	}
}
