# ./api/controllers/system.py
from fastapi import HTTPException

from app.models.api import ApiResponse
from app.routing.decorators import controller, route
from interfaces import SystemService
from app.exceptions.system import SystemOperationError
from app.di.registry import component


@component(is_dependency=True)
@controller(prefix='system',
            tags=['system'])
class SystemController:
    def __init__(self, system_service: SystemService):
        self.system_service = system_service

    @route(path='reboot',
           methods=['GET', 'POST'],
           tags=['reboot'])
    def reboot(self) -> ApiResponse:
        try:
            system_result = self.system_service.reboot()
            return ApiResponse(
                success=True,
                message=system_result.output,
                data={
                    'cmd': system_result.cmd,
                    'returncode': system_result.returncode,
                    'status': system_result.status,
                }
            )

        except SystemOperationError as e:
            raise HTTPException(
                status_code=500,
                detail={
                    'success': False,
                    'message': f"Failed to execute reboot: {str(e)}",
                    'data': None,
                }
            )

    # @route(path='shutdown',
    #        methods=['GET', 'POST'],
    #        tags=['shutdown'])
    def shutdown(self):
        try:
            return self.system_service.shutdown()
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
