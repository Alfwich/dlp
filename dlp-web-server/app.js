function app() { }

app.scope = "global";

app.on_data_loaded = null;
app.on_job_log_loaded = null;
app.on_job_status_loaded = null;

app.is_loading = false;
app.log_byte_position = 0;

app.set_scope = (new_scope) => {
	app.scope = new_scope;
}

app.load_data = (url, type) => {
	if (!app.is_loading) {
		app.log_byte_position = 0;
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

app.load_job_log = (start_bytes = 0) => {
	if (app.data.id) {
		fetch("processing/" + app.data.id + "/log.txt", {
			method: "GET",
			headers: {
				"Range": "bytes=" + start_bytes + "-"
			},
		})
			.then((response) => {
				if (response.status >= 200 && response.status < 300) {
					var content_range_header = response.headers.get("Content-Range");
					var content_range_parts = !!content_range_header ? content_range_header.split("/") : [];
					if (content_range_parts.length > 1) {
						var next_byte = parseInt(content_range_parts[1]);
						if (!isNaN(next_byte)) {
							app.log_byte_position = parseInt(next_byte);
						}
					}
					return response.text();
				} else {
					return "";
				}
			})
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
		})
			.then((response) => {
				if (app.on_job_status_loaded) {
					app.on_job_status_loaded(response.status);
				}

				app.load_job_log(app.log_byte_position);
				if (response.status != 200) {
					var interval = app.log_byte_position > 0 ? 250 : 1000;
					setTimeout(() => {
						app.load_job_status();
					}, interval);
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

