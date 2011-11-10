# encoding: UTF-8
from lxml import etree
from copy import deepcopy
import os, os.path, shutil
import difflib

def filepath(): return os.path.abspath(os.path.dirname(__file__))
def filedir(x): return os.path.abspath(os.path.join(filepath(),x))


class FolderPatch(object):
    def __init__(self, iface, patchdir):
        self.iface = iface
        if patchdir[-1] == "/": patchdir = patchdir[:-1]
        self.patch_name = os.path.basename(patchdir)
        expected_file = self.patch_name + ".xml"
        self.patch_dir = None
        for root, dirs, files in os.walk(patchdir):
            if expected_file in files:
                self.patch_dir = root
                break
        if self.patch_dir is None:
            self.iface.error("No pude encontrar %s en ninguna subcarpeta del parche." % expected_file)
            self.patch_dir = patchdir

        patch_file = os.path.join(self.patch_dir, expected_file)
        
        self.encoding = "iso-8859-15"
        self.parser = etree.XMLParser(
                        ns_clean=False,
                        encoding=self.encoding,
                        recover=True, # .. recover funciona y parsea cuasi cualquier cosa.
                        remove_blank_text=True,
                        )
        self.tree = etree.parse(patch_file, self.parser)
        self.root = self.tree.getroot()
    
    def patch_folder(self, folder):
        for addfile in self.root.xpath("/modifications/addFile"):
            path = addfile.get("path")
            filename = addfile.get("name")
            
            pathname = os.path.join(path, filename)
            self.iface.debug("Copiando %s . . ." % filename)
            src = os.path.join(self.patch_dir,filename)
            dst = os.path.join(folder,pathname)
            dst_parent = os.path.dirname(dst)
            if not os.path.exists(dst_parent):
                os.makedirs(dst_parent)
            
            shutil.copy(src, dst)
                
        for patchscript in self.root.xpath("/modifications/patchScript"):
            path = patchscript.get("path")
            filename = patchscript.get("name")
            
            pathname = os.path.join(path, filename)
            src = os.path.join(self.patch_dir,filename)
            dst = os.path.join(folder,pathname)
            
            if not os.path.exists(dst):
                self.iface.warn("Ignorando parche QS para %s (el fichero no existe)" % filename)
                continue
            self.iface.debug("Aplicando parche QS %s . . ." % filename)
            
                
            
        


def diff_folder(iface, basedir, finaldir, patchdir):
    iface.debug(u"Folder Diff $basedir:%s $finaldir:%s $patchdir:%s" % (basedir,finaldir,patchdir))
    # patchdir no debe existir
    
    
    
def patch_folder(iface, basedir, finaldir, patchdir):
    iface.debug(u"Folder Patch $basedir:%s $finaldir:%s $patchdir:%s" % (basedir,finaldir,patchdir))
    # finaldir no debe existir
    parent_finaldir = os.path.abspath(os.path.join(finaldir,".."))
    if not os.path.exists(parent_finaldir):
        iface.error("La ruta %s no existe" % parent_finaldir)
        return
    if os.path.lexists(finaldir):
        iface.error("La ruta a $finaldir %s ya existía. No se continua. " % finaldir)
        return
    if not os.path.exists(basedir):
        iface.error("La ruta %s no existe" % basedir)
        return
    if not os.path.exists(patchdir):
        iface.error("La ruta %s no existe" % patchdir)
        return
        
    os.mkdir(finaldir)
    
    for node in os.listdir(basedir):
        if node.startswith("."): continue
        src = os.path.join(basedir, node)
        if not os.path.isdir(src): continue
        dst = os.path.join(finaldir, node)
        iface.debug("Copiando %s . . . " % node)
        shutil.copytree(src,dst)
    
    fpatch = FolderPatch(iface, patchdir)
    fpatch.patch_folder(finaldir)
        

