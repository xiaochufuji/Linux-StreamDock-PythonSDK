import pyudev
# import pywinusb.hid as hid

from .ProductIDs import USBVendorIDs, USBProductIDs, g_products
from .Transport.LibUSBHIDAPI import LibUSBHIDAPI

class DeviceManager:
    streamdocks = list()

    @staticmethod
    def _get_transport(transport):
        return LibUSBHIDAPI()

    def __init__(self, transport=None):
        self.transport = self._get_transport(transport)

    def enumerate(self):
        products = g_products
        for vid, pid, class_type in products:
            found_devices = self.transport.enumerate(vid = vid, pid = pid)
            self.streamdocks.extend(list([class_type(self.transport, d) for d in found_devices]))  
        return self.streamdocks

    def listen(self):
        products = g_products

        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        flag1=0
        flag2=0
  
        for device in iter(monitor.poll, None):
            if device.action == 'add' or device.action == 'remove':
                if  device.action == 'add':
                    if flag1==0:
                        flag1=1
                        vendor_id = device.get('ID_VENDOR_ID')
                        product_id = device.get('ID_MODEL_ID')
                    elif flag1==1:
                        flag1=0
                        
                        for vid, pid, class_type in products:
                            if int(vendor_id, 16)==vid and int(product_id, 16)==pid:
                                found_devices = self.transport.enumerate(int(vendor_id, 16), int(product_id, 16))
                                # print(device.device_path)
                                for current_device in found_devices:
                                    if device.device_path.find(current_device['path'])!=-1:
                                        self.streamdocks.append(class_type(self.transport,current_device))
                                        print("创建成功(create successed!)")
                                    
                                
                elif  device.action == 'remove':
                    if flag2==0:
                        index=0
                        for streamdock in self.streamdocks:
                            if device.device_path.find(streamdock.getPath())!=-1:
                                self.streamdocks.pop(index)
                                del streamdock
                                print("删除成功(remove successed!)")
                                break
                            index=index+1
                        flag2=1
                    elif flag2==1:
                        flag2=0