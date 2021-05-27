from requests import get, session, post
from uuid import uuid4
from time import sleep, strftime, time
from os import system

class instagram:

    def __init__(self, user, password):
  
        self.data = {
        'username':user,
        'password':password,
        'device_id':str( uuid4() )
        }

        self.mobile_headers = {'User-Agent': 'Instagram 123.1.0.26.115 (iPhoneX)', 'x-ig-app-id':'936619743392459'}
        self.web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54', 'x-ig-app-id':'936619743392459', 'x-instagram-ajax': 'bd935ce3aa39' }

        self.liked = 0
        self.followed = 0

    def login(self):
    	browser = session()
    	log = browser.post("https://i.instagram.com/api/v1/accounts/login/",data=self.data, headers= self.mobile_headers)

    	if 'logged_in_user' in log.text:
    		res_cookies = browser.cookies.get_dict()
    		self.cookies  = {'sessionid':res_cookies['sessionid']}
    		self.web_headers['x-csrftoken'] = res_cookies['csrftoken']

    	return log.json()

    def get_user_id(self, username):
        return self.get_user_info_by_username(username)['id']

    def get_username(self, user_id): # Need To Delete 
        return self.get_user_info_by_user_id(user_id)['username']

    def get_user_info_by_username(self, username):
        json = get(f'https://instagram.com/{username}?__a=1', cookies = self.cookies).json()
        return json['graphql']['user']

    def get_user_info_by_user_id(self, user_id):
    	json = get(f'https://i.instagram.com/api/v1/users/{user_id}/info/', cookies=self.cookies, headers=self.web_headers).json()
    	return json['user']

    def get_post_id(self, shortcode):
    	return get(f'https://instagram.com/p/{shortcode}?__a=1').json()['graphql']['shortcode_media']['id']

    def follow_by_user_id(self, user_id):
        res = post(f'https://www.instagram.com/web/friendships/{user_id}/follow/' , cookies=self.cookies, headers=self.web_headers).json()
        return res

    def unfollow_by_user_id(self, user_id):
        res = post(f'https://www.instagram.com/web/friendships/{user_id}/unfollow/' , cookies=self.cookies, headers=self.web_headers)
        if 'Please wait' in res.text:
            return {'status':'Please Wait'}
        return res.json()

    def follow_by_username(self, username):
        user_id = self.get_user_info_by_username(username)['id']
        return self.follow_by_user_id(user_id)

    def unfollow_by_username(self, username):
        user_id = self.get_user_id(username)
        return self.unfollow_by_user_id(user_id)

    def get_followers(self, user_id):
        print('Results Will Be in self.followers_result')
        prefix = 'https://www.instagram.com/graphql/query/?'
        followers_count = self.get_user_info_by_user_id(user_id)['follower_count']
        query_hash = '5aefa9893005572d237da5068082d8d5'
        variables={"id":user_id,"include_reel":'true',"fetch_mutual":'true',"first":'100'}
        url = prefix+'query_hash='+query_hash+'&variables='+str(variables).replace("'",'"')
        json = get(url, cookies=self.cookies, headers=self.web_headers).json()['data']['user']['edge_followed_by']
        self.followers_result = [ user['node'] for user in json['edges'] ]
        still_more = json['page_info']['has_next_page']
        while still_more:
            print( f'{len(self.followers_result)}/{followers_count}' )
            sleep(0)
            variables['after'] = json['page_info']['end_cursor']
            url = prefix+'query_hash='+query_hash+'&variables='+str(variables).replace("'",'"')
            json = get(url, cookies=self.cookies,headers=self.web_headers).json()['data']['user']['edge_followed_by']
            still_more = json['page_info']['has_next_page']
            users = [ user['node'] for user in json['edges'] ]
            for user in users:
                self.followers_result.append(user)
        return self.followers_result

    def get_followings(self, user_id, sleeping_time):
        prefix = 'https://www.instagram.com/graphql/query/?'
        following_count = self.get_user_info_by_user_id(user_id)['following_count']
        query_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
        variables={"id":user_id,"include_reel":'true',"fetch_mutual":'true',"first":'100'}
        url = prefix+'query_hash='+query_hash+'&variables='+str(variables).replace("'",'"')
        json = get(url, cookies=self.cookies, headers=self.web_headers).json()['data']['user']['edge_follow']
        followings = [ user['node'] for user in json['edges'] ]
        still_more = json['page_info']['has_next_page']
        while still_more:
            sleep(sleeping_time)
            variables['after'] = json['page_info']['end_cursor']
            url = prefix+'query_hash='+query_hash+'&variables='+str(variables).replace("'",'"')
            json = get(url, cookies=self.cookies,headers=self.web_headers).json()['data']['user']['edge_follow']
            still_more = json['page_info']['has_next_page']
            users = [ user['node'] for user in json['edges'] ]
            for user in users:
                followings.append(user)
        return followings
        
        
    def get_stories_by_id(self, user_id): # Get All Stories 
        json = get( f'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}' ,cookies = self.cookies, headers = self.web_headers ).json()
        res = []
        for story in json['reels_media'][0]['items']:
                      
            if story['media_type'] == 1:
                res.append( {'type':'pic', 'src':story['image_versions2']['candidates'][0]['url']} )

            elif story['media_type']==2:
                    res.append( {'type':'vid', 'src':story['video_versions'][0]['url']} )
        return res
    
    def get_stories_by_username(self, username):
        user_id = self.get_user_id(username)
        return self.get_stories_by_id(user_id)
    

    def get_post_src(self, post_code):# you have to follow the account if it is private so you can download its posts
        info = get(f'https://instagram.com/p/{post_code}?__a=1', cookies = self.cookies ).json()['graphql']['shortcode_media']
        multi_results = []

        if info['is_video']:
            return {'type':'video','src':info['video_url']}

        elif 'edge_sidecar_to_children' in info.keys():
            
            for child in info['edge_sidecar_to_children']['edges']:
                
                if child['node']['is_video']:
                    multi_results.append(   {'type':'video','src':child['node']['video_url']}   )
                    
                else:
                    multi_results.append(  {'type':'pic','src':child['node']['display_url']}    )
                         
            return multi_results

        else:
            return {'type':'pic','src':info['display_url']}


    def like(self, post_id):
        res = post(f'https://www.instagram.com/web/likes/{post_id}/like/', cookies = self.cookies, headers = self.web_headers )
        if 'has been deleted' in res.text:
            return {'status':'Post Has Been Deleted', }
        return res.json()

    def unlike(self, post_id):
        res = post(f'https://www.instagram.com/web/likes/{post_id}/unlike/', cookies = self.cookies, headers = self.web_headers )
        if 'has been deleted' in res.text:
            return {'status':'Post Has Been Deleted', }
        return res.json()
        
    def comment_post(self, post_id, comment):
    	data = {'comment_text': comment, 'replied_to_comment_id':''}
    	res = post(f'https://www.instagram.com/web/comments/{post_id}/add/', cookies = self.cookies, headers = self.web_headers, data=data).json()
    	return res

    def get_hashtag_posts(self, hashtag_name):
        json = get(f'https://www.instagram.com/explore/tags/{hashtag_name}?__a=1', headers=self.web_headers, cookies = self.cookies).json()
        posts = []
        sections = json['data']['recent']['sections']
        for section in sections:
            section_posts = section['layout_content']['medias']
            for post in section_posts:
                posts.append(post['media'])

        return posts

    def get_hashtag_posts2(self, hashtag_name):
        json = get(f'https://www.instagram.com/explore/tags/{hashtag_name}/?__a=1', headers=self.web_headers, cookies=self.cookies).json()
        edges = json['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        posts = []

        for edge in edges:
            posts.append(edge['node'])

        return posts
