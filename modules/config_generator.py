"""
配置生成器模块
负责生成最终的Clash配置文件
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConfigGenerator:
    """Clash配置生成器"""
    
    def __init__(self):
        """初始化配置生成器"""
        self.logger = logging.getLogger(__name__)
        
        # 基础配置模板
        self.base_config = {
            'mixed-port': 7890,
            'allow-lan': True,
            'bind-address': '*',
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True,
                'ipv6': False,
                'default-nameserver': ['223.5.5.5', '119.29.29.29'],
                'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16',
                'use-hosts': True,
                'nameserver': [
                    'https://doh.pub/dns-query',
                    'https://dns.alidns.com/dns-query'
                ],
                'fallback': [
                    'https://doh.dns.sb/dns-query',
                    'https://dns.cloudflare.com/dns-query',
                    'https://dns.twnic.tw/dns-query',
                    'tls://8.8.4.4:853'
                ],
                'fallback-filter': {
                    'geoip': True,
                    'ipcidr': ['240.0.0.0/4', '0.0.0.0/32']
                }
            }
        }
        
        # 规则配置（完整规则列表来自Abandoned/sub.yaml）
        self.rules = [
            # Apple 基础规则
            "DOMAIN,dash.knjc.cfd,DIRECT",
            "DOMAIN-SUFFIX,services.googleapis.cn,手动选择",
            "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,手动选择",
            "DOMAIN,safebrowsing.urlsec.qq.com,DIRECT",
            "DOMAIN,safebrowsing.googleapis.com,DIRECT",
            "DOMAIN,developer.apple.com,手动选择",
            "DOMAIN-SUFFIX,digicert.com,手动选择",
            "DOMAIN,ocsp.apple.com,手动选择",
            "DOMAIN,ocsp.comodoca.com,手动选择",
            "DOMAIN,ocsp.usertrust.com,手动选择",
            "DOMAIN,ocsp.sectigo.com,手动选择",
            "DOMAIN,ocsp.verisign.net,手动选择",
            "DOMAIN-SUFFIX,apple-dns.net,手动选择",
            "DOMAIN,testflight.apple.com,手动选择",
            "DOMAIN,sandbox.itunes.apple.com,手动选择",
            "DOMAIN,itunes.apple.com,手动选择",
            "DOMAIN-SUFFIX,apps.apple.com,手动选择",
            "DOMAIN-SUFFIX,blobstore.apple.com,手动选择",
            "DOMAIN,cvws.icloud-content.com,手动选择",
            
            # Apple CDN 直连规则
            "DOMAIN-SUFFIX,mzstatic.com,DIRECT",
            "DOMAIN-SUFFIX,itunes.apple.com,DIRECT",
            "DOMAIN-SUFFIX,icloud.com,DIRECT",
            "DOMAIN-SUFFIX,icloud-content.com,DIRECT",
            "DOMAIN-SUFFIX,me.com,DIRECT",
            "DOMAIN-SUFFIX,aaplimg.com,DIRECT",
            "DOMAIN-SUFFIX,cdn20.com,DIRECT",
            "DOMAIN-SUFFIX,cdn-apple.com,DIRECT",
            "DOMAIN-SUFFIX,akadns.net,DIRECT",
            "DOMAIN-SUFFIX,akamaiedge.net,DIRECT",
            "DOMAIN-SUFFIX,edgekey.net,DIRECT",
            "DOMAIN-SUFFIX,mwcloudcdn.com,DIRECT",
            "DOMAIN-SUFFIX,mwcname.com,DIRECT",
            "DOMAIN-SUFFIX,apple.com,DIRECT",
            "DOMAIN-SUFFIX,apple-cloudkit.com,DIRECT",
            "DOMAIN-SUFFIX,apple-mapkit.com,DIRECT",
            
            # 中国直连网站
            "DOMAIN-SUFFIX,126.com,DIRECT",
            "DOMAIN-SUFFIX,126.net,DIRECT",
            "DOMAIN-SUFFIX,127.net,DIRECT",
            "DOMAIN-SUFFIX,163.com,DIRECT",
            "DOMAIN-SUFFIX,360buyimg.com,DIRECT",
            "DOMAIN-SUFFIX,36kr.com,DIRECT",
            "DOMAIN-SUFFIX,acfun.tv,DIRECT",
            "DOMAIN-SUFFIX,air-matters.com,DIRECT",
            "DOMAIN-SUFFIX,aixifan.com,DIRECT",
            "DOMAIN-KEYWORD,alicdn,DIRECT",
            "DOMAIN-KEYWORD,alipay,DIRECT",
            "DOMAIN-KEYWORD,taobao,DIRECT",
            "DOMAIN-SUFFIX,amap.com,DIRECT",
            "DOMAIN-SUFFIX,autonavi.com,DIRECT",
            "DOMAIN-KEYWORD,baidu,DIRECT",
            "DOMAIN-SUFFIX,bdimg.com,DIRECT",
            "DOMAIN-SUFFIX,bdstatic.com,DIRECT",
            "DOMAIN-SUFFIX,bilibili.com,DIRECT",
            "DOMAIN-SUFFIX,bilivideo.com,DIRECT",
            "DOMAIN-SUFFIX,caiyunapp.com,DIRECT",
            "DOMAIN-SUFFIX,clouddn.com,DIRECT",
            "DOMAIN-SUFFIX,cnbeta.com,DIRECT",
            "DOMAIN-SUFFIX,cnbetacdn.com,DIRECT",
            "DOMAIN-SUFFIX,cootekservice.com,DIRECT",
            "DOMAIN-SUFFIX,csdn.net,DIRECT",
            "DOMAIN-SUFFIX,ctrip.com,DIRECT",
            "DOMAIN-SUFFIX,dgtle.com,DIRECT",
            "DOMAIN-SUFFIX,dianping.com,DIRECT",
            "DOMAIN-SUFFIX,douban.com,DIRECT",
            "DOMAIN-SUFFIX,doubanio.com,DIRECT",
            "DOMAIN-SUFFIX,duokan.com,DIRECT",
            "DOMAIN-SUFFIX,easou.com,DIRECT",
            "DOMAIN-SUFFIX,ele.me,DIRECT",
            "DOMAIN-SUFFIX,feng.com,DIRECT",
            "DOMAIN-SUFFIX,fir.im,DIRECT",
            "DOMAIN-SUFFIX,frdic.com,DIRECT",
            "DOMAIN-SUFFIX,g-cores.com,DIRECT",
            "DOMAIN-SUFFIX,godic.net,DIRECT",
            "DOMAIN-SUFFIX,gtimg.com,DIRECT",
            "DOMAIN,cdn.hockeyapp.net,DIRECT",
            "DOMAIN-SUFFIX,hongxiu.com,DIRECT",
            "DOMAIN-SUFFIX,hxcdn.net,DIRECT",
            "DOMAIN-SUFFIX,iciba.com,DIRECT",
            "DOMAIN-SUFFIX,ifeng.com,DIRECT",
            "DOMAIN-SUFFIX,ifengimg.com,DIRECT",
            "DOMAIN-SUFFIX,ipip.net,DIRECT",
            "DOMAIN-SUFFIX,iqiyi.com,DIRECT",
            "DOMAIN-SUFFIX,jd.com,DIRECT",
            "DOMAIN-SUFFIX,jianshu.com,DIRECT",
            "DOMAIN-SUFFIX,knewone.com,DIRECT",
            "DOMAIN-SUFFIX,le.com,DIRECT",
            "DOMAIN-SUFFIX,lecloud.com,DIRECT",
            "DOMAIN-SUFFIX,lemicp.com,DIRECT",
            "DOMAIN-SUFFIX,licdn.com,DIRECT",
            "DOMAIN-SUFFIX,luoo.net,DIRECT",
            "DOMAIN-SUFFIX,meituan.com,DIRECT",
            "DOMAIN-SUFFIX,meituan.net,DIRECT",
            "DOMAIN-SUFFIX,mi.com,DIRECT",
            "DOMAIN-SUFFIX,miaopai.com,DIRECT",
            "DOMAIN-SUFFIX,microsoft.com,DIRECT",
            "DOMAIN-SUFFIX,microsoftonline.com,DIRECT",
            "DOMAIN-SUFFIX,miui.com,DIRECT",
            "DOMAIN-SUFFIX,miwifi.com,DIRECT",
            "DOMAIN-SUFFIX,mob.com,DIRECT",
            "DOMAIN-SUFFIX,netease.com,DIRECT",
            "DOMAIN-SUFFIX,office.com,DIRECT",
            "DOMAIN-SUFFIX,office365.com,DIRECT",
            "DOMAIN-KEYWORD,officecdn,DIRECT",
            "DOMAIN-SUFFIX,oschina.net,DIRECT",
            "DOMAIN-SUFFIX,ppsimg.com,DIRECT",
            "DOMAIN-SUFFIX,pstatp.com,DIRECT",
            "DOMAIN-SUFFIX,qcloud.com,DIRECT",
            "DOMAIN-SUFFIX,qdaily.com,DIRECT",
            "DOMAIN-SUFFIX,qdmm.com,DIRECT",
            "DOMAIN-SUFFIX,qhimg.com,DIRECT",
            "DOMAIN-SUFFIX,qhres.com,DIRECT",
            "DOMAIN-SUFFIX,qidian.com,DIRECT",
            "DOMAIN-SUFFIX,qihucdn.com,DIRECT",
            "DOMAIN-SUFFIX,qiniu.com,DIRECT",
            "DOMAIN-SUFFIX,qiniucdn.com,DIRECT",
            "DOMAIN-SUFFIX,qiyipic.com,DIRECT",
            "DOMAIN-SUFFIX,qq.com,DIRECT",
            "DOMAIN-SUFFIX,qqurl.com,DIRECT",
            "DOMAIN-SUFFIX,rarbg.to,DIRECT",
            "DOMAIN-SUFFIX,ruguoapp.com,DIRECT",
            "DOMAIN-SUFFIX,segmentfault.com,DIRECT",
            "DOMAIN-SUFFIX,sinaapp.com,DIRECT",
            "DOMAIN-SUFFIX,smzdm.com,DIRECT",
            "DOMAIN-SUFFIX,snapdrop.net,DIRECT",
            "DOMAIN-SUFFIX,sogou.com,DIRECT",
            "DOMAIN-SUFFIX,sogoucdn.com,DIRECT",
            "DOMAIN-SUFFIX,sohu.com,DIRECT",
            "DOMAIN-SUFFIX,soku.com,DIRECT",
            "DOMAIN-SUFFIX,speedtest.net,DIRECT",
            "DOMAIN-SUFFIX,sspai.com,DIRECT",
            "DOMAIN-SUFFIX,suning.com,DIRECT",
            "DOMAIN-SUFFIX,taobao.com,DIRECT",
            "DOMAIN-SUFFIX,tencent.com,DIRECT",
            "DOMAIN-SUFFIX,tenpay.com,DIRECT",
            "DOMAIN-SUFFIX,tianyancha.com,DIRECT",
            "DOMAIN-SUFFIX,tmall.com,DIRECT",
            "DOMAIN-SUFFIX,tudou.com,DIRECT",
            "DOMAIN-SUFFIX,umetrip.com,DIRECT",
            "DOMAIN-SUFFIX,upaiyun.com,DIRECT",
            "DOMAIN-SUFFIX,upyun.com,DIRECT",
            "DOMAIN-SUFFIX,veryzhun.com,DIRECT",
            "DOMAIN-SUFFIX,weather.com,DIRECT",
            "DOMAIN-SUFFIX,weibo.com,DIRECT",
            "DOMAIN-SUFFIX,xiami.com,DIRECT",
            "DOMAIN-SUFFIX,xiami.net,DIRECT",
            "DOMAIN-SUFFIX,xiaomicp.com,DIRECT",
            "DOMAIN-SUFFIX,ximalaya.com,DIRECT",
            "DOMAIN-SUFFIX,xmcdn.com,DIRECT",
            "DOMAIN-SUFFIX,xunlei.com,DIRECT",
            "DOMAIN-SUFFIX,yhd.com,DIRECT",
            "DOMAIN-SUFFIX,yihaodianimg.com,DIRECT",
            "DOMAIN-SUFFIX,yinxiang.com,DIRECT",
            "DOMAIN-SUFFIX,ykimg.com,DIRECT",
            "DOMAIN-SUFFIX,youdao.com,DIRECT",
            "DOMAIN-SUFFIX,youku.com,DIRECT",
            "DOMAIN-SUFFIX,zealer.com,DIRECT",
            "DOMAIN-SUFFIX,zhihu.com,DIRECT",
            "DOMAIN-SUFFIX,zhimg.com,DIRECT",
            "DOMAIN-SUFFIX,zimuzu.tv,DIRECT",
            "DOMAIN-SUFFIX,zoho.com,DIRECT",
            
            # 代理规则
            "DOMAIN-KEYWORD,amazon,手动选择",
            "DOMAIN-KEYWORD,google,手动选择",
            "DOMAIN-KEYWORD,gmail,手动选择",
            "DOMAIN-KEYWORD,youtube,手动选择",
            "DOMAIN-KEYWORD,facebook,手动选择",
            "DOMAIN-SUFFIX,fb.me,手动选择",
            "DOMAIN-SUFFIX,fbcdn.net,手动选择",
            "DOMAIN-KEYWORD,twitter,手动选择",
            "DOMAIN-KEYWORD,instagram,手动选择",
            "DOMAIN-KEYWORD,dropbox,手动选择",
            "DOMAIN-SUFFIX,twimg.com,手动选择",
            "DOMAIN-KEYWORD,blogspot,手动选择",
            "DOMAIN-SUFFIX,youtu.be,手动选择",
            "DOMAIN-KEYWORD,whatsapp,手动选择",
            
            # 广告拦截
            "DOMAIN-KEYWORD,admarvel,REJECT",
            "DOMAIN-KEYWORD,admaster,REJECT",
            "DOMAIN-KEYWORD,adsage,REJECT",
            "DOMAIN-KEYWORD,adsmogo,REJECT",
            "DOMAIN-KEYWORD,adsrvmedia,REJECT",
            "DOMAIN-KEYWORD,adwords,REJECT",
            "DOMAIN-KEYWORD,adservice,REJECT",
            "DOMAIN-SUFFIX,appsflyer.com,REJECT",
            "DOMAIN-KEYWORD,domob,REJECT",
            "DOMAIN-SUFFIX,doubleclick.net,REJECT",
            "DOMAIN-KEYWORD,duomeng,REJECT",
            "DOMAIN-KEYWORD,dwtrack,REJECT",
            "DOMAIN-KEYWORD,guanggao,REJECT",
            "DOMAIN-KEYWORD,lianmeng,REJECT",
            "DOMAIN-SUFFIX,mmstat.com,REJECT",
            "DOMAIN-KEYWORD,mopub,REJECT",
            "DOMAIN-KEYWORD,omgmta,REJECT",
            "DOMAIN-KEYWORD,openx,REJECT",
            "DOMAIN-KEYWORD,partnerad,REJECT",
            "DOMAIN-KEYWORD,pingfore,REJECT",
            "DOMAIN-KEYWORD,supersonicads,REJECT",
            "DOMAIN-KEYWORD,uedas,REJECT",
            "DOMAIN-KEYWORD,umeng,REJECT",
            "DOMAIN-KEYWORD,usage,REJECT",
            "DOMAIN-SUFFIX,vungle.com,REJECT",
            "DOMAIN-KEYWORD,wlmonitor,REJECT",
            "DOMAIN-KEYWORD,zjtoolbar,REJECT",
            
            # 国外常用网站
            "DOMAIN-SUFFIX,9to5mac.com,手动选择",
            "DOMAIN-SUFFIX,abpchina.org,手动选择",
            "DOMAIN-SUFFIX,adblockplus.org,手动选择",
            "DOMAIN-SUFFIX,adobe.com,手动选择",
            "DOMAIN-SUFFIX,akamaized.net,手动选择",
            "DOMAIN-SUFFIX,alfredapp.com,手动选择",
            "DOMAIN-SUFFIX,amplitude.com,手动选择",
            "DOMAIN-SUFFIX,ampproject.org,手动选择",
            "DOMAIN-SUFFIX,android.com,手动选择",
            "DOMAIN-SUFFIX,angularjs.org,手动选择",
            "DOMAIN-SUFFIX,aolcdn.com,手动选择",
            "DOMAIN-SUFFIX,apkpure.com,手动选择",
            "DOMAIN-SUFFIX,appledaily.com,手动选择",
            "DOMAIN-SUFFIX,appshopper.com,手动选择",
            "DOMAIN-SUFFIX,appspot.com,手动选择",
            "DOMAIN-SUFFIX,arcgis.com,手动选择",
            "DOMAIN-SUFFIX,archive.org,手动选择",
            "DOMAIN-SUFFIX,armorgames.com,手动选择",
            "DOMAIN-SUFFIX,aspnetcdn.com,手动选择",
            "DOMAIN-SUFFIX,att.com,手动选择",
            "DOMAIN-SUFFIX,awsstatic.com,手动选择",
            "DOMAIN-SUFFIX,azureedge.net,手动选择",
            "DOMAIN-SUFFIX,azurewebsites.net,手动选择",
            "DOMAIN-SUFFIX,bing.com,手动选择",
            "DOMAIN-SUFFIX,bintray.com,手动选择",
            "DOMAIN-SUFFIX,bit.com,手动选择",
            "DOMAIN-SUFFIX,bit.ly,手动选择",
            "DOMAIN-SUFFIX,bitbucket.org,手动选择",
            "DOMAIN-SUFFIX,bjango.com,手动选择",
            "DOMAIN-SUFFIX,bkrtx.com,手动选择",
            "DOMAIN-SUFFIX,blog.com,手动选择",
            "DOMAIN-SUFFIX,blogcdn.com,手动选择",
            "DOMAIN-SUFFIX,blogger.com,手动选择",
            "DOMAIN-SUFFIX,blogsmithmedia.com,手动选择",
            "DOMAIN-SUFFIX,blogspot.com,手动选择",
            "DOMAIN-SUFFIX,blogspot.hk,手动选择",
            "DOMAIN-SUFFIX,bloomberg.com,手动选择",
            "DOMAIN-SUFFIX,box.com,手动选择",
            "DOMAIN-SUFFIX,box.net,手动选择",
            "DOMAIN-SUFFIX,cachefly.net,手动选择",
            "DOMAIN-SUFFIX,chromium.org,手动选择",
            "DOMAIN-SUFFIX,cl.ly,手动选择",
            "DOMAIN-SUFFIX,cloudflare.com,手动选择",
            "DOMAIN-SUFFIX,cloudfront.net,手动选择",
            "DOMAIN-SUFFIX,cloudmagic.com,手动选择",
            "DOMAIN-SUFFIX,cmail19.com,手动选择",
            "DOMAIN-SUFFIX,cnet.com,手动选择",
            "DOMAIN-SUFFIX,cocoapods.org,手动选择",
            "DOMAIN-SUFFIX,comodoca.com,手动选择",
            "DOMAIN-SUFFIX,crashlytics.com,手动选择",
            "DOMAIN-SUFFIX,culturedcode.com,手动选择",
            "DOMAIN-SUFFIX,d.pr,手动选择",
            "DOMAIN-SUFFIX,danilo.to,手动选择",
            "DOMAIN-SUFFIX,dayone.me,手动选择",
            "DOMAIN-SUFFIX,db.tt,手动选择",
            "DOMAIN-SUFFIX,deskconnect.com,手动选择",
            "DOMAIN-SUFFIX,disq.us,手动选择",
            "DOMAIN-SUFFIX,disqus.com,手动选择",
            "DOMAIN-SUFFIX,disquscdn.com,手动选择",
            "DOMAIN-SUFFIX,dnsimple.com,手动选择",
            "DOMAIN-SUFFIX,docker.com,手动选择",
            "DOMAIN-SUFFIX,dribbble.com,手动选择",
            "DOMAIN-SUFFIX,droplr.com,手动选择",
            "DOMAIN-SUFFIX,duckduckgo.com,手动选择",
            "DOMAIN-SUFFIX,dueapp.com,手动选择",
            "DOMAIN-SUFFIX,dytt8.net,手动选择",
            "DOMAIN-SUFFIX,edgecastcdn.net,手动选择",
            "DOMAIN-SUFFIX,edgekey.net,手动选择",
            "DOMAIN-SUFFIX,edgesuite.net,手动选择",
            "DOMAIN-SUFFIX,engadget.com,手动选择",
            "DOMAIN-SUFFIX,entrust.net,手动选择",
            "DOMAIN-SUFFIX,eurekavpt.com,手动选择",
            "DOMAIN-SUFFIX,evernote.com,手动选择",
            "DOMAIN-SUFFIX,fabric.io,手动选择",
            "DOMAIN-SUFFIX,fast.com,手动选择",
            "DOMAIN-SUFFIX,fastly.net,手动选择",
            "DOMAIN-SUFFIX,fc2.com,手动选择",
            "DOMAIN-SUFFIX,feedburner.com,手动选择",
            "DOMAIN-SUFFIX,feedly.com,手动选择",
            "DOMAIN-SUFFIX,feedsportal.com,手动选择",
            "DOMAIN-SUFFIX,fiftythree.com,手动选择",
            "DOMAIN-SUFFIX,firebaseio.com,手动选择",
            "DOMAIN-SUFFIX,flexibits.com,手动选择",
            "DOMAIN-SUFFIX,flickr.com,手动选择",
            "DOMAIN-SUFFIX,flipboard.com,手动选择",
            "DOMAIN-SUFFIX,g.co,手动选择",
            "DOMAIN-SUFFIX,gabia.net,手动选择",
            "DOMAIN-SUFFIX,geni.us,手动选择",
            "DOMAIN-SUFFIX,gfx.ms,手动选择",
            "DOMAIN-SUFFIX,ggpht.com,手动选择",
            "DOMAIN-SUFFIX,ghostnoteapp.com,手动选择",
            "DOMAIN-SUFFIX,git.io,手动选择",
            "DOMAIN-KEYWORD,github,手动选择",
            "DOMAIN-SUFFIX,globalsign.com,手动选择",
            "DOMAIN-SUFFIX,gmodules.com,手动选择",
            "DOMAIN-SUFFIX,godaddy.com,手动选择",
            "DOMAIN-SUFFIX,golang.org,手动选择",
            "DOMAIN-SUFFIX,gongm.in,手动选择",
            "DOMAIN-SUFFIX,goo.gl,手动选择",
            "DOMAIN-SUFFIX,goodreaders.com,手动选择",
            "DOMAIN-SUFFIX,goodreads.com,手动选择",
            "DOMAIN-SUFFIX,gravatar.com,手动选择",
            "DOMAIN-SUFFIX,gstatic.com,手动选择",
            "DOMAIN-SUFFIX,gvt0.com,手动选择",
            "DOMAIN-SUFFIX,hockeyapp.net,手动选择",
            "DOMAIN-SUFFIX,hotmail.com,手动选择",
            "DOMAIN-SUFFIX,icons8.com,手动选择",
            "DOMAIN-SUFFIX,ifixit.com,手动选择",
            "DOMAIN-SUFFIX,ift.tt,手动选择",
            "DOMAIN-SUFFIX,ifttt.com,手动选择",
            "DOMAIN-SUFFIX,iherb.com,手动选择",
            "DOMAIN-SUFFIX,imageshack.us,手动选择",
            "DOMAIN-SUFFIX,img.ly,手动选择",
            "DOMAIN-SUFFIX,imgur.com,手动选择",
            "DOMAIN-SUFFIX,imore.com,手动选择",
            "DOMAIN-SUFFIX,instapaper.com,手动选择",
            "DOMAIN-SUFFIX,ipn.li,手动选择",
            "DOMAIN-SUFFIX,is.gd,手动选择",
            "DOMAIN-SUFFIX,issuu.com,手动选择",
            "DOMAIN-SUFFIX,itgonglun.com,手动选择",
            "DOMAIN-SUFFIX,itun.es,手动选择",
            "DOMAIN-SUFFIX,ixquick.com,手动选择",
            "DOMAIN-SUFFIX,j.mp,手动选择",
            "DOMAIN-SUFFIX,js.revsci.net,手动选择",
            "DOMAIN-SUFFIX,jshint.com,手动选择",
            "DOMAIN-SUFFIX,jtvnw.net,手动选择",
            "DOMAIN-SUFFIX,justgetflux.com,手动选择",
            "DOMAIN-SUFFIX,kat.cr,手动选择",
            "DOMAIN-SUFFIX,klip.me,手动选择",
            "DOMAIN-SUFFIX,libsyn.com,手动选择",
            "DOMAIN-SUFFIX,linkedin.com,手动选择",
            "DOMAIN-SUFFIX,line-apps.com,手动选择",
            "DOMAIN-SUFFIX,linode.com,手动选择",
            "DOMAIN-SUFFIX,lithium.com,手动选择",
            "DOMAIN-SUFFIX,littlehj.com,手动选择",
            "DOMAIN-SUFFIX,live.com,手动选择",
            "DOMAIN-SUFFIX,live.net,手动选择",
            "DOMAIN-SUFFIX,livefilestore.com,手动选择",
            "DOMAIN-SUFFIX,llnwd.net,手动选择",
            "DOMAIN-SUFFIX,macid.co,手动选择",
            "DOMAIN-SUFFIX,macromedia.com,手动选择",
            "DOMAIN-SUFFIX,macrumors.com,手动选择",
            "DOMAIN-SUFFIX,mashable.com,手动选择",
            "DOMAIN-SUFFIX,mathjax.org,手动选择",
            "DOMAIN-SUFFIX,medium.com,手动选择",
            "DOMAIN-SUFFIX,mega.co.nz,手动选择",
            "DOMAIN-SUFFIX,mega.nz,手动选择",
            "DOMAIN-SUFFIX,megaupload.com,手动选择",
            "DOMAIN-SUFFIX,microsofttranslator.com,手动选择",
            "DOMAIN-SUFFIX,mindnode.com,手动选择",
            "DOMAIN-SUFFIX,mobile01.com,手动选择",
            "DOMAIN-SUFFIX,modmyi.com,手动选择",
            "DOMAIN-SUFFIX,msedge.net,手动选择",
            "DOMAIN-SUFFIX,myfontastic.com,手动选择",
            "DOMAIN-SUFFIX,name.com,手动选择",
            "DOMAIN-SUFFIX,nextmedia.com,手动选择",
            "DOMAIN-SUFFIX,nsstatic.net,手动选择",
            "DOMAIN-SUFFIX,nssurge.com,手动选择",
            "DOMAIN-SUFFIX,nyt.com,手动选择",
            "DOMAIN-SUFFIX,nytimes.com,手动选择",
            "DOMAIN-SUFFIX,omnigroup.com,手动选择",
            "DOMAIN-SUFFIX,onedrive.com,手动选择",
            "DOMAIN-SUFFIX,onenote.com,手动选择",
            "DOMAIN-SUFFIX,ooyala.com,手动选择",
            "DOMAIN-SUFFIX,openvpn.net,手动选择",
            "DOMAIN-SUFFIX,openwrt.org,手动选择",
            "DOMAIN-SUFFIX,orkut.com,手动选择",
            "DOMAIN-SUFFIX,osxdaily.com,手动选择",
            "DOMAIN-SUFFIX,outlook.com,手动选择",
            "DOMAIN-SUFFIX,ow.ly,手动选择",
            "DOMAIN-SUFFIX,paddleapi.com,手动选择",
            "DOMAIN-SUFFIX,parallels.com,手动选择",
            "DOMAIN-SUFFIX,parse.com,手动选择",
            "DOMAIN-SUFFIX,pdfexpert.com,手动选择",
            "DOMAIN-SUFFIX,periscope.tv,手动选择",
            "DOMAIN-SUFFIX,pinboard.in,手动选择",
            "DOMAIN-SUFFIX,pinterest.com,手动选择",
            "DOMAIN-SUFFIX,pixelmator.com,手动选择",
            "DOMAIN-SUFFIX,pixiv.net,手动选择",
            "DOMAIN-SUFFIX,playpcesor.com,手动选择",
            "DOMAIN-SUFFIX,playstation.com,手动选择",
            "DOMAIN-SUFFIX,playstation.com.hk,手动选择",
            "DOMAIN-SUFFIX,playstation.net,手动选择",
            "DOMAIN-SUFFIX,playstationnetwork.com,手动选择",
            "DOMAIN-SUFFIX,pushwoosh.com,手动选择",
            "DOMAIN-SUFFIX,rime.im,手动选择",
            "DOMAIN-SUFFIX,servebom.com,手动选择",
            "DOMAIN-SUFFIX,sfx.ms,手动选择",
            "DOMAIN-SUFFIX,shadowsocks.org,手动选择",
            "DOMAIN-SUFFIX,sharethis.com,手动选择",
            "DOMAIN-SUFFIX,shazam.com,手动选择",
            "DOMAIN-SUFFIX,skype.com,手动选择",
            "DOMAIN-SUFFIX,smartmailcloud.com,手动选择",
            "DOMAIN-SUFFIX,smartmailcloud.com,手动选择",
            "DOMAIN-SUFFIX,sndcdn.com,手动选择",
            "DOMAIN-SUFFIX,sony.com,手动选择",
            "DOMAIN-SUFFIX,soundcloud.com,手动选择",
            "DOMAIN-SUFFIX,sourceforge.net,手动选择",
            "DOMAIN-SUFFIX,spotify.com,手动选择",
            "DOMAIN-SUFFIX,squarespace.com,手动选择",
            "DOMAIN-SUFFIX,sstatic.net,手动选择",
            "DOMAIN-SUFFIX,st.luluku.pw,手动选择",
            "DOMAIN-SUFFIX,stackoverflow.com,手动选择",
            "DOMAIN-SUFFIX,startpage.com,手动选择",
            "DOMAIN-SUFFIX,staticflickr.com,手动选择",
            "DOMAIN-SUFFIX,steamcommunity.com,手动选择",
            "DOMAIN-SUFFIX,symauth.com,手动选择",
            "DOMAIN-SUFFIX,symcb.com,手动选择",
            "DOMAIN-SUFFIX,symcd.com,手动选择",
            "DOMAIN-SUFFIX,tapbots.com,手动选择",
            "DOMAIN-SUFFIX,tapbots.net,手动选择",
            "DOMAIN-SUFFIX,tdesktop.com,手动选择",
            "DOMAIN-SUFFIX,techcrunch.com,手动选择",
            "DOMAIN-SUFFIX,techsmith.com,手动选择",
            "DOMAIN-SUFFIX,thepiratebay.org,手动选择",
            "DOMAIN-SUFFIX,theverge.com,手动选择",
            "DOMAIN-SUFFIX,time.com,手动选择",
            "DOMAIN-SUFFIX,timeinc.net,手动选择",
            "DOMAIN-SUFFIX,tiny.cc,手动选择",
            "DOMAIN-SUFFIX,tinypic.com,手动选择",
            "DOMAIN-SUFFIX,tmblr.co,手动选择",
            "DOMAIN-SUFFIX,todoist.com,手动选择",
            "DOMAIN-SUFFIX,trello.com,手动选择",
            "DOMAIN-SUFFIX,trustasiassl.com,手动选择",
            "DOMAIN-SUFFIX,tumblr.co,手动选择",
            "DOMAIN-SUFFIX,tumblr.com,手动选择",
            "DOMAIN-SUFFIX,tweetdeck.com,手动选择",
            "DOMAIN-SUFFIX,tweetmarker.net,手动选择",
            "DOMAIN-SUFFIX,twitch.tv,手动选择",
            "DOMAIN-SUFFIX,txmblr.com,手动选择",
            "DOMAIN-SUFFIX,typekit.net,手动选择",
            "DOMAIN-SUFFIX,ubertags.com,手动选择",
            "DOMAIN-SUFFIX,ublock.org,手动选择",
            "DOMAIN-SUFFIX,ubnt.com,手动选择",
            "DOMAIN-SUFFIX,ulyssesapp.com,手动选择",
            "DOMAIN-SUFFIX,urchin.com,手动选择",
            "DOMAIN-SUFFIX,usertrust.com,手动选择",
            "DOMAIN-SUFFIX,v.gd,手动选择",
            "DOMAIN-SUFFIX,v2ex.com,手动选择",
            "DOMAIN-SUFFIX,vimeo.com,手动选择",
            "DOMAIN-SUFFIX,vimeocdn.com,手动选择",
            "DOMAIN-SUFFIX,vine.co,手动选择",
            "DOMAIN-SUFFIX,vivaldi.com,手动选择",
            "DOMAIN-SUFFIX,vox-cdn.com,手动选择",
            "DOMAIN-SUFFIX,vsco.co,手动选择",
            "DOMAIN-SUFFIX,vultr.com,手动选择",
            "DOMAIN-SUFFIX,w.org,手动选择",
            "DOMAIN-SUFFIX,w3schools.com,手动选择",
            "DOMAIN-SUFFIX,webtype.com,手动选择",
            "DOMAIN-SUFFIX,wikiwand.com,手动选择",
            "DOMAIN-SUFFIX,wikileaks.org,手动选择",
            "DOMAIN-SUFFIX,wikimedia.org,手动选择",
            "DOMAIN-SUFFIX,wikipedia.com,手动选择",
            "DOMAIN-SUFFIX,wikipedia.org,手动选择",
            "DOMAIN-SUFFIX,windows.com,手动选择",
            "DOMAIN-SUFFIX,windows.net,手动选择",
            "DOMAIN-SUFFIX,wire.com,手动选择",
            "DOMAIN-SUFFIX,wordpress.com,手动选择",
            "DOMAIN-SUFFIX,workflowy.com,手动选择",
            "DOMAIN-SUFFIX,wp.com,手动选择",
            "DOMAIN-SUFFIX,wsj.com,手动选择",
            "DOMAIN-SUFFIX,wsj.net,手动选择",
            "DOMAIN-SUFFIX,xda-developers.com,手动选择",
            "DOMAIN-SUFFIX,xeeno.com,手动选择",
            "DOMAIN-SUFFIX,xiti.com,手动选择",
            "DOMAIN-SUFFIX,yahoo.com,手动选择",
            "DOMAIN-SUFFIX,yimg.com,手动选择",
            "DOMAIN-SUFFIX,ying.com,手动选择",
            "DOMAIN-SUFFIX,yoyo.org,手动选择",
            "DOMAIN-SUFFIX,ytimg.com,手动选择",
            "DOMAIN-SUFFIX,telegra.ph,手动选择",
            "DOMAIN-SUFFIX,telegram.org,手动选择",
            
            # IP-CIDR 规则（Telegram）
            "IP-CIDR,91.108.4.0/22,手动选择,no-resolve",
            "IP-CIDR,91.108.8.0/21,手动选择,no-resolve",
            "IP-CIDR,91.108.16.0/22,手动选择,no-resolve",
            "IP-CIDR,91.108.56.0/22,手动选择,no-resolve",
            "IP-CIDR,149.154.160.0/20,手动选择,no-resolve",
            "IP-CIDR6,2001:67c:4e8::/48,手动选择,no-resolve",
            "IP-CIDR6,2001:b28:f23d::/48,手动选择,no-resolve",
            "IP-CIDR6,2001:b28:f23f::/48,手动选择,no-resolve",
            
            # 国内IP段
            "IP-CIDR,120.232.181.162/32,手动选择,no-resolve",
            "IP-CIDR,120.241.147.226/32,手动选择,no-resolve",
            "IP-CIDR,120.253.253.226/32,手动选择,no-resolve",
            "IP-CIDR,120.253.255.162/32,手动选择,no-resolve",
            "IP-CIDR,120.253.255.34/32,手动选择,no-resolve",
            "IP-CIDR,120.253.255.98/32,手动选择,no-resolve",
            "IP-CIDR,180.163.150.162/32,手动选择,no-resolve",
            "IP-CIDR,180.163.150.34/32,手动选择,no-resolve",
            "IP-CIDR,180.163.151.162/32,手动选择,no-resolve",
            "IP-CIDR,180.163.151.34/32,手动选择,no-resolve",
            "IP-CIDR,203.208.39.0/24,手动选择,no-resolve",
            "IP-CIDR,203.208.40.0/24,手动选择,no-resolve",
            "IP-CIDR,203.208.41.0/24,手动选择,no-resolve",
            "IP-CIDR,203.208.43.0/24,手动选择,no-resolve",
            "IP-CIDR,203.208.50.0/24,手动选择,no-resolve",
            "IP-CIDR,220.181.174.162/32,手动选择,no-resolve",
            "IP-CIDR,220.181.174.226/32,手动选择,no-resolve",
            "IP-CIDR,220.181.174.34/32,手动选择,no-resolve",
            
            # 本地网络和特殊规则
            "DOMAIN,injections.adguard.org,DIRECT",
            "DOMAIN,local.adguard.org,DIRECT",
            "DOMAIN-SUFFIX,local,DIRECT",
            "IP-CIDR,127.0.0.0/8,DIRECT",
            "IP-CIDR,172.16.0.0/12,DIRECT",
            "IP-CIDR,192.168.0.0/16,DIRECT",
            "IP-CIDR,10.0.0.0/8,DIRECT",
            "IP-CIDR,17.0.0.0/8,DIRECT",
            "IP-CIDR,100.64.0.0/10,DIRECT",
            "IP-CIDR,224.0.0.0/4,DIRECT",
            "IP-CIDR6,fe80::/10,DIRECT",
            "DOMAIN-SUFFIX,cn,DIRECT",
            "DOMAIN-KEYWORD,-cn,DIRECT",
            "GEOIP,CN,DIRECT",
        ]
        
    def generate_config(self, proxies: List[Dict[str, Any]], 
                       output_file: Path) -> bool:
        """
        生成最终的Clash配置文件
        
        Args:
            proxies: 代理配置列表
            output_file: 输出文件路径
            
        Returns:
            bool: 是否成功生成
        """
        try:
            self.logger.info(f"开始生成配置文件: {output_file}")
            
            # 获取代理名称列表
            proxy_names = [proxy.get('name', 'Unknown') for proxy in proxies]
            self.logger.info(f"共有 {len(proxy_names)} 个代理节点")
            
            # 生成配置文件内容
            content_lines = []
            
            # 添加基础配置
            content_lines.extend(self._generate_base_config_lines())
            
            # 添加proxy-groups部分
            content_lines.extend(self._generate_proxy_groups_lines(proxy_names))
            
            # 添加rules部分
            content_lines.extend(self._generate_rules_lines())
            
            # 写入文件
            content = '\n'.join(content_lines)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"配置文件已生成: {output_file}")
            self.logger.info(f"文件大小: {output_file.stat().st_size} 字节")
            return True
            
        except Exception as e:
            self.logger.error(f"生成配置文件失败: {str(e)}")
            return False
            
    def _generate_base_config_lines(self) -> List[str]:
        """
        生成基础配置行
        
        Returns:
            List[str]: 基础配置行列表
        """
        lines = []
        
        # 添加基本配置
        for key, value in self.base_config.items():
            if key == 'dns':
                continue  # 单独处理DNS配置
            elif isinstance(value, bool):
                lines.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, str):
                lines.append(f"{key}: '{value}'")
            else:
                lines.append(f"{key}: {value}")
                
        # 添加DNS配置
        lines.append('dns:')
        dns = self.base_config['dns']
        lines.append('    enable: true')
        lines.append('    ipv6: false')
        lines.append(f"    default-nameserver: [{', '.join([f'{x}' for x in dns['default-nameserver']])}]")
        lines.append('    enhanced-mode: fake-ip')
        lines.append('    fake-ip-range: 198.18.0.1/16')
        lines.append('    use-hosts: true')
        lines.append(f"    nameserver: {dns['nameserver']}")
        lines.append(f"    fallback: {dns['fallback']}")
        lines.append(f"    fallback-filter: {dns['fallback-filter']}")
        
        return lines
        
    def _generate_proxies_lines(self, proxies: List[Dict[str, Any]]) -> List[str]:
        """
         生成proxies配置行
         
         Args:
             proxies: 代理配置列表
             
         Returns:
             List[str]: proxies配置行列表
         """
        lines = ['proxies:']
        
        for proxy in proxies:
            try:
                # 检查是否为字符串（已经是JSON格式）
                if isinstance(proxy, str):
                    lines.append(f"  - {proxy}")
                    continue
                    
                # 创建代理配置副本
                proxy_copy = {}
                for key, value in proxy.items():
                    if isinstance(value, bool):
                        proxy_copy[key] = value
                    elif isinstance(value, (int, float, str)):
                        proxy_copy[key] = value
                    else:
                        proxy_copy[key] = value
                            
                # 转换为JSON字符串，使用紧凑格式
                proxy_json = json.dumps(proxy_copy, ensure_ascii=False, separators=(',', ':'))
                lines.append(f"  - {proxy_json}")
                    
            except Exception as e:
                proxy_name = proxy.get('name', 'Unknown') if isinstance(proxy, dict) else str(proxy)
                self.logger.warning(f"转换代理配置失败: {proxy_name}, 错误: {str(e)}")
                continue
                    
        return lines
        
    def _generate_proxy_groups_lines(self, proxy_names: List[str]) -> List[str]:
        """
        生成proxy-groups配置行
        
        Args:
            proxy_names: 代理名称列表
            
        Returns:
            List[str]: proxy-groups配置行列表
        """
        lines = ['proxy-groups:']
        
        # 手动选择组
        lines.append(self._create_group_line('手动选择', 'select', 
                                           ['自动选择', '故障转移'] + proxy_names))
        
        # 自动选择组
        lines.append(self._create_group_line('自动选择', 'url-test', proxy_names,
                                           url='http://www.gstatic.com/generate_204',
                                           interval=86400))
        
        # 故障转移组
        lines.append(self._create_group_line('故障转移', 'fallback', proxy_names,
                                           url='http://www.gstatic.com/generate_204',
                                           interval=7200))
        
        return lines
        
    def _create_group_line(self, name: str, group_type: str, proxies: List[str],
                          url: Optional[str] = None, interval: Optional[int] = None) -> str:
        """
         创建代理组配置行
         
         Args:
             name: 组名称
             group_type: 组类型
             proxies: 代理列表
             url: 测试URL
             interval: 测试间隔
             
         Returns:
             str: 代理组配置行
         """
        # 构建代理列表（不带额外引号）
        proxies_list = []
        for proxy_name in proxies:
            proxies_list.append(proxy_name)
            
        # 构建组数据
        group_data = {
            'name': name,
            'type': group_type,
            'proxies': proxies_list
        }
        
        if url:
            group_data['url'] = url
        if interval:
            group_data['interval'] = interval
            
        # 转换为JSON，使用紧凑格式
        group_json = json.dumps(group_data, ensure_ascii=False, separators=(',', ':'))
        return f"  - {group_json}"
        
    def _generate_rules_lines(self) -> List[str]:
        """
        生成rules配置行
        
        Returns:
            List[str]: rules配置行列表
        """
        lines = ['rules:']
        
        for rule in self.rules:
            if isinstance(rule, str):
                # 规则已经是完整格式的字符串
                lines.append(f"    - '{rule}'")
            else:
                # 兼容旧格式的元组
                rule_type, rule_value, proxy = rule
                lines.append(f"    - '{rule_type},{rule_value},{proxy}'")
            
        # 添加最终的MATCH规则
        lines.append("    - 'MATCH,手动选择'")
        
        return lines
        
    def generate_config_preview(self, proxies: List[Dict[str, Any]], 
                              output_file: Path) -> str:
        """
        生成配置预览（不写入文件）
        
        Args:
            proxies: 代理配置列表
            output_file: 输出文件路径
            
        Returns:
            str: 配置文件预览内容
        """
        # 临时生成文件内容
        temp_path = Path(str(output_file) + '.preview')
        if self.generate_config(proxies, temp_path):
            with open(temp_path, 'r', encoding='utf-8') as f:
                preview = f.read()
            temp_path.unlink()  # 删除预览文件
            return preview
        else:
            return "预览生成失败"
            
    def get_config_info(self, output_file: Path) -> Dict[str, Any]:
        """
        获取生成的配置信息
        
        Args:
            output_file: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置信息
        """
        info = {
            'file_path': str(output_file),
            'exists': output_file.exists(),
            'proxies_count': 0,
            'proxy_groups_count': 0,
            'rules_count': 0,
            'file_size': 0
        }
        
        if output_file.exists():
            info['file_size'] = output_file.stat().st_size
            
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 统计配置项
                info['proxies_count'] = content.count('  - {')
                # 简化统计逻辑
                if 'proxy-groups:' in content:
                    proxy_groups_section = content.split('proxy-groups:')[1].split('rules:')[0] if 'rules:' in content else content.split('proxy-groups:')[1]
                    info['proxy_groups_count'] = proxy_groups_section.count('  - {')
                else:
                    info['proxy_groups_count'] = 0
                info['rules_count'] = content.count("    - '")
                
            except Exception as e:
                self.logger.error(f"读取配置信息失败: {str(e)}")
                
        return info