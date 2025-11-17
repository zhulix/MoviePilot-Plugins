import requests
from datetime import datetime
from typing import Any, List, Dict, Tuple, Optional

from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType


class JavaUploaderNotifier(_PluginBase):
    """
    Java 上传器通知插件

    整理完成后推送到 Java Cloud Uploader 服务
    """

    # 插件名称
    plugin_name = "Java上传器通知"
    # 插件描述
    plugin_desc = "整理完成后推送到 Java Cloud Uploader 服务，自动上传到云盘"
    # 插件图标
    plugin_icon = "cloud-upload.png"
    # 插件版本
    plugin_version = "1.1"
    # 插件作者
    plugin_author = "Claude"
    # 作者主页
    author_url = "https://github.com"
    # 插件配置项ID前缀
    plugin_config_prefix = "javauploadernotifier_"
    # 加载顺序
    plugin_order = 20
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _api_url = ""
    _api_token = ""
    _only_success = True
    _retry_times = 3
    _timeout = 10

    def init_plugin(self, config: dict = None):
        """
        初始化插件
        """
        if config:
            self._enabled = config.get("enabled", False)
            self._api_url = config.get("api_url", "").rstrip("/")
            self._api_token = config.get("api_token", "")
            self._only_success = config.get("only_success", True)
            self._retry_times = config.get("retry_times", 3)
            self._timeout = config.get("timeout", 10)

        logger.info(f"Java上传器通知插件初始化完成: enabled={self._enabled}, api_url={self._api_url}")

    def get_state(self) -> bool:
        """
        获取插件运行状态
        """
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        定义远程控制命令
        """
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """
        获取插件API
        """
        return [{
            "path": "/test",
            "endpoint": self.test_connection,
            "methods": ["GET"],
            "summary": "测试连接",
            "description": "测试与Java API的连接"
        }]

    def test_connection(self) -> dict:
        """
        测试与Java API的连接
        """
        if not self._api_url or not self._api_token:
            return {
                "success": False,
                "message": "API地址或Token未配置"
            }

        try:
            # 发送测试请求
            headers = {
                "Content-Type": "application/json",
                "X-API-Token": self._api_token
            }

            # 构造测试数据
            test_data = {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                f"{self._api_url}/test",
                json=test_data,
                headers=headers,
                timeout=self._timeout
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "连接成功",
                    "response": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败: HTTP {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"连接异常: {str(e)}"
            }

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、数据结构
        """
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'only_success',
                                            'label': '仅推送成功的整理',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'api_url',
                                            'label': 'Java API 地址',
                                            'placeholder': 'http://localhost:8085/api/webhook',
                                            'hint': '请填写完整的API地址，不包含末尾斜杠'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'api_token',
                                            'label': 'API Token',
                                            'placeholder': 'change-me-please',
                                            'type': 'password'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'retry_times',
                                            'label': '重试次数',
                                            'type': 'number',
                                            'hint': '推送失败时的重试次数'
                                        }
                                    }
                                ]
                            },
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'timeout',
                                            'label': '超时时间(秒)',
                                            'type': 'number',
                                            'hint': 'API请求的超时时间'
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12
                                },
                                'content': [
                                    {
                                        'component': 'VAlert',
                                        'props': {
                                            'type': 'info',
                                            'variant': 'tonal',
                                            'text': '整理完成后会自动推送到配置的 Java API 地址，创建云盘上传任务。'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "api_url": "http://localhost:8085/api/webhook",
            "api_token": "change-me-please",
            "only_success": True,
            "retry_times": 3,
            "timeout": 10
        }

    def get_page(self) -> List[dict]:
        """
        拼装插件详情页面，需要返回页面配置，同时附带数据
        """
        # 获取推送统计
        stats = self.get_data("stats") or {"total": 0, "success": 0, "failed": 0}

        return [
            {
                'component': 'VRow',
                'content': [
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 4
                        },
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'text': f'总推送次数\n{stats["total"]}'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 4
                        },
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'color': 'success'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'text': f'成功次数\n{stats["success"]}'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 4
                        },
                        'content': [
                            {
                                'component': 'VCard',
                                'props': {
                                    'variant': 'tonal',
                                    'color': 'error'
                                },
                                'content': [
                                    {
                                        'component': 'VCardText',
                                        'props': {
                                            'class': 'text-center'
                                        },
                                        'text': f'失败次数\n{stats["failed"]}'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

    @eventmanager.register(EventType.TransferComplete)
    def on_transfer_complete(self, event: Event):
        """
        整理完成事件处理
        """
        if not self._enabled:
            return

        if not self._api_url or not self._api_token:
            logger.warning("Java上传器通知插件未配置 API 地址或 Token")
            return

        try:
            event_data = event.event_data
            if not event_data:
                return

            # 获取整理信息
            context = event_data.get("context")
            mediainfo = event_data.get("mediainfo")
            transferinfo = event_data.get("transferinfo")

            if not transferinfo:
                logger.warning("整理信息为空，跳过推送")
                return

            # 检查是否只推送成功的整理
            if self._only_success and not transferinfo.success:
                logger.info(f"整理失败，跳过推送: {transferinfo.target_path if transferinfo.target_path else 'unknown'}")
                return

            # 获取 TransferHistory ID
            transfer_history_id = self._get_transfer_history_id(transferinfo)

            # 构造推送数据
            payload = {
                "transferHistoryId": transfer_history_id,
                "title": mediainfo.title if mediainfo else "",
                "year": str(mediainfo.year) if mediainfo and mediainfo.year else "",
                "type": mediainfo.type.value if mediainfo and mediainfo.type else "未知",
                "season": transferinfo.season if hasattr(transferinfo, 'season') else None,
                "episode": transferinfo.episode if hasattr(transferinfo, 'episode') else None,
                "tmdbId": mediainfo.tmdb_id if mediainfo else None,
                "imdbId": mediainfo.imdb_id if mediainfo else None,
                "targetPath": str(transferinfo.target_path) if transferinfo.target_path else "",
                "fileSize": transferinfo.total_size if hasattr(transferinfo, 'total_size') else 0,
                "fileCount": len(transferinfo.file_list_new) if hasattr(transferinfo, 'file_list_new') and transferinfo.file_list_new else 0,
                "success": transferinfo.success if hasattr(transferinfo, 'success') else True,
                "message": transferinfo.message if hasattr(transferinfo, 'message') else "",
                "timestamp": datetime.now().isoformat()
            }

            # 推送到 Java API
            logger.info(f"准备推送到 Java API: {payload.get('title', 'unknown')} - {payload.get('targetPath', 'unknown')}")
            self._push_to_api(payload)

        except Exception as e:
            logger.error(f"整理完成事件处理异常: {str(e)}", exc_info=True)
            self._update_stats(failed=True)

    def _get_transfer_history_id(self, transferinfo) -> Optional[int]:
        """
        获取 TransferHistory ID
        """
        try:
            from app.db.transferhistory_oper import TransferHistoryOper

            # 通过目标路径查询
            if hasattr(transferinfo, 'target_path') and transferinfo.target_path:
                target_path = str(transferinfo.target_path)
                oper = TransferHistoryOper()
                # 查询最近的匹配记录
                history = oper.get_by_dest(target_path)
                if history:
                    return history.id
        except Exception as e:
            logger.error(f"获取 TransferHistory ID 失败: {str(e)}")

        # 如果无法获取，返回 None
        return None

    def _push_to_api(self, data: dict):
        """
        推送到外部 API，支持重试
        """
        retry_count = 0
        last_error = None

        while retry_count <= self._retry_times:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Token": self._api_token
                }

                response = requests.post(
                    self._api_url,
                    json=data,
                    headers=headers,
                    timeout=self._timeout
                )

                if response.status_code == 200:
                    logger.info(f"推送成功: {data.get('title', 'unknown')}")
                    result = response.json()
                    logger.debug(f"响应: {result}")
                    self._update_stats(success=True)
                    return
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"推送失败(尝试 {retry_count + 1}/{self._retry_times + 1}): {last_error}")

            except requests.exceptions.Timeout:
                last_error = "请求超时"
                logger.warning(f"推送超时(尝试 {retry_count + 1}/{self._retry_times + 1})")
            except requests.exceptions.ConnectionError:
                last_error = f"无法连接到 {self._api_url}"
                logger.warning(f"连接失败(尝试 {retry_count + 1}/{self._retry_times + 1}): {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"推送异常(尝试 {retry_count + 1}/{self._retry_times + 1}): {last_error}")

            retry_count += 1

        # 所有重试都失败
        logger.error(f"推送最终失败，已重试 {self._retry_times} 次: {last_error}")
        self._update_stats(failed=True)

    def _update_stats(self, success: bool = False, failed: bool = False):
        """
        更新统计数据
        """
        try:
            stats = self.get_data("stats") or {"total": 0, "success": 0, "failed": 0}
            stats["total"] += 1
            if success:
                stats["success"] += 1
            if failed:
                stats["failed"] += 1
            self.save_data("stats", stats)
        except Exception as e:
            logger.error(f"更新统计数据失败: {str(e)}")

    def stop_service(self):
        """
        退出插件
        """
        pass
