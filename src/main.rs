use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct UploadInfo {
    uploads: String,
}

#[derive(Deserialize, Debug)]
struct ChannelContentDetails {
    #[serde(rename = "relatedPlaylists")]
    related_playlists: UploadInfo,
}

#[derive(Deserialize, Debug)]
struct ChannelItem {
    #[serde(rename = "contentDetails")]
    content_details: ChannelContentDetails,
}

#[derive(Deserialize, Debug)]
struct ChannelInfoResponse {
    items: Vec<ChannelItem>,
}

impl ChannelInfoResponse {
    fn uploads_id(&self) -> String {
        self.items[0].content_details.related_playlists.uploads.clone()
    }
}

#[derive(Deserialize, Debug)]
struct ContentDetails {
    #[serde(rename = "videoPublishedAt")]
    published_at: String,
    #[serde(rename = "videoId")]
    video_id: String,
}

#[derive(Deserialize, Debug)]
struct Item {
    #[serde(rename = "contentDetails")]
    details: ContentDetails,
    id: String,
    etag: String,
}

#[derive(Deserialize, Debug)]
struct PageInfo {
    #[serde(rename = "resultsPerPage")]
    results_per_page: u64,
    #[serde(rename = "totalResults")]
    total_results: u64,
}

#[derive(Deserialize, Debug)]
struct ItemsList {
    items: Vec<Item>,
    #[serde(rename = "nextPageToken")]
    next_page_token: Option<String>,
    #[serde(rename = "pageInfo")]
    page_info: PageInfo,
}

async fn fetch_channel_info(key: &str, username: &str) -> String {
    let url = format!("https://www.googleapis.com/youtube/v3/channels?part={part}&key={key}&forUsername={username}",
        part="contentDetails",
        key=key,
        username=username);
    let content = reqwest::get(&url)
        .await
        .unwrap()
        .json::<ChannelInfoResponse>()
        .await
        .unwrap();
    content.uploads_id()
}

async fn fetch_items(key: &str, uploads_id: &str) {
    let url = format!("https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part={part}&maxResults=50&playlistId={playlist_id}",
        part="contentDetails",
        key=key,
        playlist_id=uploads_id);
    let content = reqwest::get(&url)
        .await
        .unwrap()
        .json::<ItemsList>()
        .await
        .unwrap();
    println!("{:#?}", content);
}


#[tokio::main]
async fn main() {
    dotenv::dotenv().ok();
    let key = std::env::var("GOOGLE_API_KEY").unwrap();
    let username = "outsidexbox";
    let uploads_id = fetch_channel_info(&key, username).await;
    fetch_items(&key, &uploads_id).await;
}
