<Query Kind="Program">
  <NuGetReference Prerelease="true">linqtotwitter</NuGetReference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <Namespace>LinqToTwitter</Namespace>
  <Namespace>LinqToTwitter.Security</Namespace>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
</Query>

void Main()
{
    Directory.SetCurrentDirectory(Path.GetDirectoryName(Util.CurrentQueryPath));

    var config = JObject.Parse(File.ReadAllText(@"../appsettings.Development.json"));

    var auth = new SingleUserAuthorizer {
        CredentialStore = new SingleUserInMemoryCredentialStore {
            ConsumerKey = config["Twitter"]["ConsumerKey"].ToString(),
            ConsumerSecret = config["Twitter"]["ConsumerSecret"].ToString(),
            AccessToken = config["Twitter"]["AccessToken"].ToString(),
            AccessTokenSecret = config["Twitter"]["AccessTokenSecret"].ToString()
        }
    };

    var twitter = new TwitterContext(auth);

    var statuses = twitter.Status
        .Where(s => s.Type == StatusType.User && s.TweetMode == TweetMode.Extended)
        // .Select(s => s.FullText)
        .ToList();
  
// statuses.Dump();

    FormatStatusText(statuses[2]).Dump();
    FormatStatusText(statuses[7]).Dump();
    FormatStatusText(statuses[14]).Dump();
}

private string FormatStatusText(Status status)
        {
            var text = status.FullText;
            var transformedText = Regex.Replace(text, @"(@([^\s\:\,\.\u2014]+))", @"<a href=""https://twitter.com/$2"">$1</a>");
            return transformedText;
        }