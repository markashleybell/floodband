using System;
using System.Linq;
using System.Text.RegularExpressions;
using LinqToTwitter;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;

namespace floodband.Controllers
{
    public class HomeController : Controller
    {
        private const string _statusesCacheKey = "statuses";

        private readonly IConfiguration _configuration;
        private readonly IMemoryCache _cache;

        public HomeController(IConfiguration configuration, IMemoryCache cache)
        {
            _configuration = configuration;
            _cache = cache;
        }

        public IActionResult Index() => View();

        public IActionResult Music() => View();

        public IActionResult Links() => View();

        public IActionResult Contact() => View();

        public IActionResult Gigs() => View();

        public IActionResult Statuses() => GetStatuses();

        private JsonResult GetStatuses()
        {
            if (!_cache.TryGetValue(_statusesCacheKey, out JsonResult result))
            {
                var cacheEntryOptions = new MemoryCacheEntryOptions()
                    .SetAbsoluteExpiration(TimeSpan.FromMinutes(1));

                var auth = new SingleUserAuthorizer {
                    CredentialStore = new SingleUserInMemoryCredentialStore {
                        ConsumerKey = _configuration.GetSection("Twitter")["ConsumerKey"],
                        ConsumerSecret = _configuration.GetSection("Twitter")["ConsumerSecret"],
                        AccessToken = _configuration.GetSection("Twitter")["AccessToken"],
                        AccessTokenSecret = _configuration.GetSection("Twitter")["AccessTokenSecret"]
                    }
                };

                var twitter = new TwitterContext(auth);

                var statuses = twitter.Status
                    .Where(s => s.Type == StatusType.User && s.TweetMode == TweetMode.Extended)
                    .Take(4)
                    .ToList();

                var transformedStatuses = statuses.Select(s => new {
                    created_at = s.CreatedAt,
                    text = FormatStatusText(s)
                });

                result = Json(new { statuses = transformedStatuses });

                _cache.Set(_statusesCacheKey, result, cacheEntryOptions);
            }

            return result;
        }

        private string FormatStatusText(Status status)
        {
            var options = RegexOptions.IgnoreCase | RegexOptions.Multiline;

            // Replace Twitter handles with profile links
            var text = Regex.Replace(status.FullText, @"(@([^\s\:\,\.\u2014]+))", @"<a href=""https://twitter.com/$2"">$1</a>");

            // Replace shortened links with actual URLs
            foreach (var link in status.Entities.UrlEntities)
            {
                text = Regex.Replace(text, link.Url, $@"<a href=""{link.ExpandedUrl}"">{link.DisplayUrl}</a>", options);
            }

            // Replace image links with something a bit more obvious
            foreach (var media in status.Entities.MediaEntities)
            {
                text = Regex.Replace(text, media.Url, $@"<a href=""{media.MediaUrlHttps}"">View Photo</a>", options);
            }

            return text;
        }
    }
}
