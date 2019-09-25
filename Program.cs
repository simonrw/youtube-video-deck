using System;
using System.Threading.Tasks;
using dotenv.net;
using Google.Apis.YouTube.v3;
using Google.Apis.Services;


namespace youtube_video_deck
{
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            DotEnv.Config();
            new Program().Run().Wait();
        }

        private async Task Run() {
            var ApiKey = Environment.GetEnvironmentVariable("API_KEY");
            if (String.IsNullOrEmpty(ApiKey)) {
                Console.WriteLine("Error fetching api key");
            } else {
                Console.WriteLine(String.Format("API key: {0}", ApiKey));
                var yt = new YouTubeService(new BaseClientService.Initializer
                    {
                        ApplicationName = "My Youtube Video Deck",
                        ApiKey = ApiKey,
                    });

                var channelsListRequest = yt.Channels.List("contentDetails");
                channelsListRequest.ForUsername = "mindriot101";

                var channelsListResponse = await channelsListRequest.ExecuteAsync();
                if (channelsListResponse.Items == null) {
                    Console.WriteLine("Invalid items found");
                    return;
                }

                foreach (var item in channelsListResponse.Items) {
                    var stats = item.Statistics;
                    if (stats == null) {
                        continue;
                    }
                    Console.WriteLine(String.Format("Channel has {0} subscribers", stats.SubscriberCount));
                }
            }
        }
    }
}
