from typing import Any, List, Dict, Tuple

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType
from app.modules.themoviedb.tmdbv3api import Search
from app.schemas.types import MediaType


class YyTest(_PluginBase):
    # 插件名称
    plugin_name = "我的测试插件"
    # 插件描述
    plugin_desc = "测试插件"
    # 插件图标
    plugin_icon = "chatgpt.png"
    # 主题色
    plugin_color = "#74AA9C"
    # 插件版本
    plugin_version = "1.3"
    # 插件作者
    plugin_author = "yyned2501"
    # 作者主页
    author_url = "https://github.com/yyned2501"
    # 插件配置项ID前缀
    plugin_config_prefix = "yytest_"
    # 加载顺序
    plugin_order = 15
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    openai = None
    _enabled = False
    _proxy = False
    _recognize = False
    _openai_url = None
    _openai_key = None

    def init_plugin(self, config: dict = None):
        if config:
            self._enabled = config.get("enabled")
            self.search = Search()

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                ],
            }
        ], {
            "enabled": False,
        }

    def get_page(self) -> List[dict]:
        pass

    def search_movies(self, title: str, year: str) -> List[dict]:
        """
        查询模糊匹配的所有电影TMDB信息
        """
        if not title:
            return []
        ret_infos = []
        if year:
            movies = self.search.movies(term=title, year=year, adult=True) or []
        else:
            movies = self.search.movies(term=title, adult=True) or []
        for movie in movies:
            if title in movie.get("title"):
                movie["media_type"] = MediaType.MOVIE
                ret_infos.append(movie)
        return ret_infos

    def search_tvs(self, title: str, year: str) -> List[dict]:
        """
        查询模糊匹配的所有电视剧TMDB信息
        """
        if not title:
            return []
        ret_infos = []
        if year:
            tvs = self.search.tv_shows(term=title, release_year=year, adult=True) or []
        else:
            tvs = self.search.tv_shows(term=title, adult=True) or []
        for tv in tvs:
            if title in tv.get("name"):
                tv["media_type"] = MediaType.TV
                ret_infos.append(tv)
        return ret_infos

    @eventmanager.register(EventType.NameRecognize)
    def recognize(self, event: Event):
        """
        监听识别事件，使用ChatGPT辅助识别名称
        """
        if not event.event_data:
            return
        title = event.event_data.get("title")
        if not title:
            return
        # 收到事件后需要立码返回，避免主程序等待
        if not self._enabled:
            eventmanager.send_event(EventType.NameRecognizeResult, {"title": title})
            return
        # 调用ChatGPT
        movie = self.search_movies(title)
        tv = self.search_tvs(title)
        if len(movie)>0:
            eventmanager.send_event(
                EventType.NameRecognizeResult,
                {
                    "title": title,
                    "name": movie[0].get("title"),
                    "year": movie[0].get("year"),
                    "season": movie[0].get("season"),
                    "episode": movie[0].get("episode"),
                },
            )
        elif len(movie)>0:
            eventmanager.send_event(
                EventType.NameRecognizeResult,
                {
                    "title": title,
                    "name": tv[0].get("title"),
                    "year": tv[0].get("year"),
                    "season": tv[0].get("season"),
                    "episode": tv[0].get("episode"),
                },
            )


    def stop_service(self):
        """
        退出插件
        """
        pass
