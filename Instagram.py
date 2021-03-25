from requests import get, session, post
from uuid import uuid4
from time import sleep, strftime


class instagram:

    def __init__(self, user, password):
  
        data = {
        'username':user,
        'password':password,
        'device_id':str( uuid4() )
        }

        self.mobile_headers = {'User-Agent': 'Instagram 123.1.0.26.115 (iPhoneX)', 'x-ig-app-id':'936619743392459'}
        self.web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54', 'x-ig-app-id':'936619743392459'}
        

        # Get cookies
        browser = session()
        log = browser.post("https://i.instagram.com/api/v1/accounts/login/",data=data, headers= self.mobile_headers)

        if 'logged_in_user' in log.text:
            res_cookies = browser.cookies.get_dict()
            self.cookies  = {'sessionid':res_cookies['sessionid']}
            self.web_headers['x-csrftoken'] = res_cookies['csrftoken']
            print(f'Logged As {user} Successfully')

        else:
            print(log.json()['message'])


    def get_user_id(self, username):
        json = get(f'https://instagram.com/{username}?__a=1', cookies = self.cookies).json()
        return json['logging_page_id'].split('_')[1]




    def get_stories(self, user_id): # Get All Stories 
        json = get( f'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}' ,cookies = self.cookies, headers = self.web_headers ).json()
        res = []
        for story in json['reels_media'][0]['items']:
                      
            if story['media_type'] == 1:
                res.append( {'type':'pic', 'src':story['image_versions2']['candidates'][0]['url']} )

            elif story['media_type']==2:
                    res.append( {'type':'vid', 'src':story['video_versions'][0]['url']} )


        return res


    def get_post_src(self, post_id):# you have to follow the account if it is private so you can download its posts
        info = get(f'https://instagram.com/p/{post_id}?__a=1', cookies = self.cookies ).json()['graphql']['shortcode_media']
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


    def get_hashtag_posts(self, hashtag_name):
        json = get(f'https://www.instagram.com/explore/tags/{hashtag_name}?__a=1', headers=self.web_headers, cookies=self.cookies).json()
        posts = []
        for i in json['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            i = i['node']
            shortcode = i['shortcode']
            posts.append( {'post_id':i['id'], 'shortcode':shortcode, 'url':f'https://instagram.com/p/{shortcode}', 'owner_id': i['owner']['id'] } )
        return posts


    def like_post(self, post_id):
        res = post(f'https://www.instagram.com/web/likes/{post_id}/like/', cookies = self.cookies, headers = self.web_headers ).text
        if res == '{"status":"ok"}':
            return True
        else:
            return res

    def like_hashtag(self, hashtag_name):
        posts = self.get_hashtag_posts(hashtag_name)
        for Post in posts:
            res = self.like_post(Post['post_id'])
            if res == True:
                print( 'Done: ' + Post['url'] )
            else:
                if input(res+'\nSleep? (y/n): ') == 'y':
                    print('Sleeping For 5min\nStarted At: '+ strftime('%H:%M:%S'))
                    sleep(60*5)
