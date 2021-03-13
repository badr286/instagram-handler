from requests import get, session, post
from uuid import uuid4


class instagram:

    def __init__(self, user,password):

        self.done = []
        self.app_id = '936619743392459'
                
        data = {
        'username':user,
        'password':password,
        'device_id':str( uuid4() )
        }

        browser = session()
        phone_agent = 'Instagram 123.1.0.26.115 (iPhoneX)'
        log = browser.post("https://i.instagram.com/api/v1/accounts/login/",data=data, headers={'User-Agent': phone_agent})

        if 'logged_in_user' in log.text:
            self.sessionid = browser.cookies.get_dict()['sessionid']

        else:
            print(log.json()['message'])




    def get_stories(self, user_id): # Get All Stories 
        json = get( f'https://i.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}' ,cookies = {'sessionid':self.sessionid}, headers={'x-ig-app-id':self.app_id}).json()
        res = []
        for story in json['reels_media'][0]['items']:
                      
            if story['media_type'] == 1:
                res.append( {'type':'pic', 'src':story['image_versions2']['candidates'][0]['url']} )

            elif story['media_type']==2:
                    res.append( {'type':'vid', 'src':story['video_versions'][0]['url']} )


        return res


    def get_post_src(self, post_id):# you have to follow the account if it is private so you can download its posts
        info = get(f'https://instagram.com/p/{post_id}?__a=1', cookies = {'sessionid':self.sessionid} ).json()['graphql']['shortcode_media']
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
        
                
        
