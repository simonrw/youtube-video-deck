use serde::Deserialize;
use warp::{self, path, Filter};

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
        self.items[0]
            .content_details
            .related_playlists
            .uploads
            .clone()
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

struct MyApi {
    key: String,
}

impl MyApi {
    fn new(key: String) -> Self {
        MyApi { key }
    }

    async fn fetch_channel_info(&self, username: &str) -> String {
        let url = format!("https://www.googleapis.com/youtube/v3/channels?part={part}&key={key}&forUsername={username}",
            part="contentDetails",
            key=&self.key,
            username=username);
        let content = reqwest::get(&url)
            .await
            .unwrap()
            .json::<ChannelInfoResponse>()
            .await
            .unwrap();
        content.uploads_id()
    }

    async fn fetch_items(&self, uploads_id: &str, page_token: Option<&str>) {
        let url = match page_token {
                None => format!("https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part={part}&maxResults=50&playlistId={playlist_id}",
                    part="contentDetails",
                    key=&self.key,
                    playlist_id=uploads_id),
                Some(t) => format!("https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part={part}&maxResults=50&playlistId={playlist_id}&pageToken={page_token}",
                    part="contentDetails",
                    key=&self.key,
                    page_token=t,
                    playlist_id=uploads_id),
            };
        let content = reqwest::get(&url)
            .await
            .unwrap()
            .json::<ItemsList>()
            .await
            .unwrap();
        println!("{:#?}", content);
    }
}

#[tokio::main]
async fn main() {

    // let hello = path!("hello" / String)
    //     .map(|name| format!("Hello {}", name));
    let routes = warp::any().map(|| {
        "Hello world"
    });
    warp::serve(routes).run(([127, 0, 0, 1], 3030))

    // dotenv::dotenv().ok();
    // let key = std::env::var("GOOGLE_API_KEY").unwrap();
    // let username = "outsidexbox";

    // let client = MyApi::new(key);

    // let uploads_id = client.fetch_channel_info(username).await;
    // client.fetch_items(&uploads_id, None).await;
}
