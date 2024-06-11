function app() {}

app.scope = "global";

app.on_data_loaded = null;
app.on_job_log_loaded = null;
app.on_job_status_loaded = null;

app.is_loading = false;

app.set_scope = (new_scope) => {
	app.scope = new_scope;
}

app.load_data = (url, type) => {
	if (!app.is_loading) {
		app.is_loading = fetch("data.php", {
			method: "POST",
			body: JSON.stringify({
				url: url,
				type: type,
				scope: app.scope,
				remove_idx: null,
			}),
			headers: {
				"Content-type": "application/json; charset=UTF-8"
			}
		})
		.then((response) => response.json())
		.then((json) => {
			app.data = json;
			if (app.on_data_loaded) {
				app.on_data_loaded();
			}
			app.is_loading = false;

			if (json) {
				app.load_job_status();
			}
		}); 
	}
}

app.load_job_log = (request_all=false) => {
	if (app.data.id) {
		fetch("processing/" + app.data.id + "/log.txt", { 
			method: "GET",
			headers: request_all ? {} : {
				"Range": "-128"
			}
		} )
		.then((response) => response.text())
		.then((body) => {
			if (app.on_job_log_loaded) {
				app.on_job_log_loaded(body);
			}
		});
	}
}

app.load_job_status = () => {
	if (app.data.id) {
		fetch("processing/" + app.data.id + "/done", { 
			method: "GET", 
		} )
		.then((response) => {
			if (app.on_job_status_loaded) {
				app.on_job_status_loaded(response.status == 200);
			}

			app.load_job_log(response.status == 200);
			if (response.status != 200) {
				setTimeout(() => {
					app.load_job_status();
				}, 1000);
			}
		});
	}
}

app.remove_video = (video_idx) => {
	fetch("data.php", {
		method: "POST",
		body: JSON.stringify({
			url: "",
			type: "",
			scope: app.scope,
			remove_idx: video_idx,
		}),
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	})
	.then((response) => response.json())
	.then((json) => {
		app.data = json;
		if (app.on_data_loaded) {
			app.on_data_loaded();
		}
	}); 
}

