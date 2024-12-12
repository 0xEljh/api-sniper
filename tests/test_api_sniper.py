import pytest
import responses
import json
from urllib.parse import unquote
from api_sniper import APISniper, SniperConfig
from api_sniper.exceptions import AuthError, RequestError


@pytest.fixture
def config():
    return SniperConfig(
        base_url="https://api.example.com",
        timeout=5,
        retry_attempts=2
    )

@pytest.fixture
def sniper(config):
    return APISniper(config)

@responses.activate
def test_get_request(sniper):
    """Test basic GET request functionality."""
    # Mock the response
    responses.add(
        responses.GET,
        "https://api.example.com/api/test",
        json={"data": "test_value"},
        status=200
    )
    
    # Make request
    response = sniper.get("/api/test")
    
    # Verify response
    assert response == {"data": "test_value"}
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.example.com/api/test"

@responses.activate
def test_authentication_flow(sniper):
    """Test authentication flow with token."""
    # Mock auth endpoint
    responses.add(
        responses.POST,
        "https://api.example.com/auth/login",
        json={"access_token": "test_token", "token_type": "Bearer"},
        status=200
    )
    
    # Mock protected endpoint
    def request_callback(request):
        if "Authorization" in request.headers:
            if request.headers["Authorization"] == "Bearer test_token":
                return (200, {}, '{"data": "protected"}')
        return (401, {}, '{"error": "unauthorized"}')
    
    responses.add_callback(
        responses.GET,
        "https://api.example.com/api/protected",
        callback=request_callback
    )
    
    # Test unauthorized access
    with pytest.raises(RequestError):
        sniper.get("/api/protected")
    
    # Login and get token
    sniper.auth.login("test_user", "test_pass")
    
    # Test authorized access
    response = sniper.get("/api/protected")
    assert response == {"data": "protected"}

@responses.activate
def test_retry_logic(sniper):
    """Test retry logic on failed requests."""
    # Mock endpoint that fails twice then succeeds
    responses.add(
        responses.GET,
        "https://api.example.com/api/flaky",
        status=500
    )
    responses.add(
        responses.GET,
        "https://api.example.com/api/flaky",
        status=500
    )
    responses.add(
        responses.GET,
        "https://api.example.com/api/flaky",
        json={"data": "success"},
        status=200
    )
    
    # Request should succeed after retries
    response = sniper.get("/api/flaky")
    assert response == {"data": "success"}
    assert len(responses.calls) == 3

@responses.activate
def test_request_pattern_recording(sniper):
    """Test request pattern recording and replay."""
    # Mock endpoint
    responses.add(
        responses.POST,
        "https://api.example.com/api/data",
        json={"status": "recorded"},
        status=200
    )
    
    # Record pattern
    sniper.record_request_pattern(
        "test_pattern",
        method="POST",
        url="/api/data",
        json={"test": "data"}
    )
    
    # Replay pattern
    response = sniper.replay_request("test_pattern")
    assert response == {"status": "recorded"}
    
    # Verify request
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.example.com/api/data"
    assert responses.calls[0].request.body == b'{"test": "data"}'

def test_user_agent_rotation(config):
    """Test user agent rotation functionality."""
    # Configure with user agents
    config.user_agent_rotation = True
    config.user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/89.0"
    ]
    
    # Create multiple instances to test rotation
    snipers = [APISniper(config) for _ in range(5)]
    
    # Verify user agents are being rotated
    user_agents = [
        sniper.session.headers["User-Agent"]
        for sniper in snipers
    ]
    
    # Check that we're using agents from our list
    assert all(ua in config.user_agents for ua in user_agents)
    # Check that we got some rotation (not all same agent)
    assert len(set(user_agents)) > 1



@pytest.fixture
def x_config():
    return SniperConfig(
        base_url="https://api.x.com",
        timeout=10,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "x-twitter-client-language": "en-GB",
            "x-twitter-active-user": "yes",
            "Origin": "https://x.com",
            "DNT": "1",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Referer": "https://x.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers"
        }
    )

@pytest.fixture
def x_sniper(x_config):
    sniper = APISniper(x_config)
    # Set the bearer token
    sniper.set_token("AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA")
    # Set additional headers that would normally come from cookies/session
    sniper.session.headers.update({
        "x-guest-token": "1867204288591896762",
        "x-client-transaction-id": "8pzdNL4naFq/bXYssuKcKqyQwTCZlNSfmhaakcilJs/oDNINpmlrUoGqPtnOcNeD8T13+fGvSUdwo4CjpLrLRUJJ89BB8Q"
    })
    return sniper

@responses.activate
def test_x_user_by_screen_name(x_sniper):
    """Test specific X (Twitter) GraphQL API request for user by screen name."""
    
    # Construct the exact query parameters
    variables = {"screen_name": "elonmusk"}
    features = {
        "hidden_profile_subscriptions_enabled": True,
        "profile_label_improvements_pcf_label_in_post_enabled": False,
        "rweb_tipjar_consumption_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "subscriptions_verification_info_is_identity_verified_enabled": True,
        "subscriptions_verification_info_verified_since_enabled": True,
        "highlights_tweets_tab_ui_enabled": True,
        "responsive_web_twitter_article_notes_tab_enabled": True,
        "subscriptions_feature_can_gift_premium": True,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True
    }
    field_toggles = {"withAuxiliaryUserLabels": False}
    
    # Mock the expected response
    mock_response = {
        "data": {
            "user": {
                "result": {
                    "id": "44196397",
                    "rest_id": "44196397",
                    "name": "Elon Musk",
                    "screen_name": "elonmusk"
                }
            }
        }
    }
    
    # Add the mock response
    responses.add(
        responses.GET,
        "https://api.x.com/graphql/QGIw94L0abhuohrr76cSbw/UserByScreenName",
        json=mock_response,
        status=200,
        match=[
            responses.matchers.query_param_matcher({
                'variables': json.dumps(variables),
                'features': json.dumps(features),
                'fieldToggles': json.dumps(field_toggles)
            })
        ]
    )
    
    # Make the request using our API Sniper
    endpoint = "/graphql/QGIw94L0abhuohrr76cSbw/UserByScreenName"
    params = {
        'variables': json.dumps(variables),
        'features': json.dumps(features),
        'fieldToggles': json.dumps(field_toggles)
    }
    
    response = x_sniper.get(endpoint, params=params)
    
    # Verify the response
    assert response == mock_response
    assert len(responses.calls) == 1
    
    # Verify request headers
    request = responses.calls[0].request
    assert request.headers['Authorization'] == f"Bearer {x_sniper.auth._token}"
    assert request.headers['x-guest-token'] == "1867204288591896762"
    assert request.headers['content-type'] == "application/json"
    assert request.headers['Origin'] == "https://x.com"
    
    # Verify URL and parameters
    assert "UserByScreenName" in request.url
    assert "variables" in request.url
    assert "features" in request.url
    assert "fieldToggles" in request.url
