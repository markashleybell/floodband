using LinqToTwitter;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using System;
using System.Linq;
using System.Text.RegularExpressions;

namespace floodband.Controllers
{
    public class HomeController : Controller
    {
        private IConfiguration _configuration;
        private MemoryCache _cache;

        public HomeController(IConfiguration configuration) =>
            _configuration = configuration;

        public IActionResult Index() => View();

        public IActionResult Music() => View();

        public IActionResult Links() => View();

        public IActionResult Contact() => View();

        public IActionResult Gigs() => View();

        public IActionResult Statuses()
        {
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
                .Take(4).ToList();

            var transformedStatuses = statuses.Select(s => {
                var text = s.FullText;
                return new {
                    created_at = s.CreatedAt,
                    text = s.FullText
                };
            });

            return Json(new {
                statuses = transformedStatuses
            });

            //        s['text'] = re.sub(r"(@([^\s\:\,\.\u2014]+))", r'<a href="https://twitter.com/\2">\1</a>', s['text'], 0, re.IGNORECASE | re.MULTILINE)
            //        for u in s['entities']['urls']:
            //            s['text'] = re.sub(u['url'], r'<a href="' + u['expanded_url'] + '">' + u['display_url'] + '</a>', s['text'], 0, re.IGNORECASE | re.MULTILINE)
            //        if 'media' in s['entities']:
            //            for u in s['entities']['media']:
            //                s['text'] = re.sub(u['url'], '', s['text'], 0, re.IGNORECASE | re.MULTILINE)

            //    projection = [{ 'created_at': s['created_at'], 'text': s['text'].strip() }
            //            for s in statuses]
        }

        private string FormatStatusText(Status status)
        {
            var text = status.FullText;
            var transformedText = Regex.Replace(text, @"(@([^\s\:\,\.\u2014]+))", @"<a href=""https://twitter.com/\2"">\1</a>");
            return transformedText;
        }
    }
}
