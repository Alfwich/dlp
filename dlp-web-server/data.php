<?php
//ini_set('display_errors', '1');
//ini_set('display_startup_errors', '1');
//error_reporting(E_ALL);

function endsWith( $haystack, $needle ) {
    $length = strlen( $needle );
    if( !$length ) {
        return true;
    }
    return substr( $haystack, -$length ) === $needle;
};

function content_filter_fn($var) {
	return $var != "." && $var != "..";
};

function sort_fn($fileA, $fileB) {
	return filemtime($fileA) < filemtime($fileB);
};

$job_id = null;
$files = array();

$raw_data = file_get_contents('php://input');
$in_data = json_decode($raw_data, true);

$in_data['scope'] = preg_replace("/[^a-zA-Z0-9]+/", "", substr($in_data['scope'], 0, 20));

$url = $in_data['url'];
$type = $in_data['type'];
$remove_idx = $in_data['remove_idx'];
$scope = $in_data['scope'];

if (empty($scope)) {
	$scope = "global";
}

if (!empty($url) && !empty($type) && ($type == "mp3" || $type == "mp4" || $type == "any")) {
	foreach ($in_data as $key => &$value) {
		$value = base64_encode($value);
	}
	unset($value);
	$job = curl_init();
	curl_setopt($job, CURLOPT_URL, "localhost/" . json_encode($in_data));
	curl_setopt($job, CURLOPT_PORT, 4141);
	curl_setopt($job, CURLOPT_VERBOSE, 0);
	curl_setopt($job, CURLOPT_RETURNTRANSFER, 1);
	$id = curl_exec($job);
	curl_close($job);
} else if (is_dir("./content/" . $scope) && isset($remove_idx)) {
	$cwd = getcwd();
	chdir("./content/" . $scope);
	$raw_files = scandir(".");
	usort($raw_files, "sort_fn");
	$files = array_filter($raw_files, "content_filter_fn");
	unlink(array_values($files)[$remove_idx]);
	chdir($cwd);
}


if (is_dir("./content/" . $scope)) {
	$cwd = getcwd();
	chdir("./content/" . $scope);
	$raw_files = scandir(".");
	usort($raw_files, "sort_fn");
	$files = array_filter($raw_files, "content_filter_fn");
	chdir($cwd);
}

$data = array(
	"id" => $id,
	"videos" => array_values($files),
	"scope" => $scope,
);

echo json_encode($data);
?>
